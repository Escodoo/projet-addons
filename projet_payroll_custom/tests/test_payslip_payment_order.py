# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPayslipPaymentOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        company = env.company

        cls.payment_account = env["account.account"].create(
            {
                "name": "Payroll Payable (Test)",
                "code": "TST99900",
                "account_type": "liability_payable",
                "reconcile": True,
                "company_id": company.id,
            }
        )
        cls.offset_account = env["account.account"].create(
            {
                "name": "Payroll Expense (Test)",
                "code": "TST99901",
                "account_type": "expense",
                "reconcile": False,
                "company_id": company.id,
            }
        )

        payment_mode = env["account.payment.mode"].search(
            [("payment_type", "=", "outbound"), ("payment_order_ok", "=", True)],
            limit=1,
        )
        cls.payment_mode = payment_mode

        cls.journal = env["account.journal"].search(
            [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
        )

        cls.move = env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cls.journal.id,
                "date": fields.Date.today(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Payroll Expense",
                            "account_id": cls.offset_account.id,
                            "debit": 1000.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Payroll Payable",
                            "account_id": cls.payment_account.id,
                            "debit": 0.0,
                            "credit": 1000.0,
                        },
                    ),
                ],
            }
        )
        cls.move.action_post()

        cls.move_second = env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cls.journal.id,
                "date": fields.Date.today(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Payroll Expense 2",
                            "account_id": cls.offset_account.id,
                            "debit": 500.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Payroll Payable 2",
                            "account_id": cls.payment_account.id,
                            "debit": 0.0,
                            "credit": 500.0,
                        },
                    ),
                ],
            }
        )
        cls.move_second.action_post()

        employee = env["hr.employee"].create({"name": "Test Employee"})
        employee_second = env["hr.employee"].create({"name": "Test Employee 2"})

        cls.payslip_run = env["hr.payslip.run"].create(
            {
                "name": "Test Payroll Batch",
                "date_start": fields.Date.today().replace(day=1),
                "date_end": fields.Date.today(),
                "company_id": company.id,
                "payment_mode_id": cls.payment_mode.id,
                "payment_account_id": cls.payment_account.id,
            }
        )

        cls.payslip = env["hr.payslip"].create(
            {
                "name": "Test Payslip",
                "employee_id": employee.id,
                "company_id": company.id,
                "payslip_run_id": cls.payslip_run.id,
                "move_id": cls.move.id,
                "date_from": cls.payslip_run.date_start,
                "date_to": cls.payslip_run.date_end,
            }
        )

        cls.payslip_second = env["hr.payslip"].create(
            {
                "name": "Test Payslip 2",
                "employee_id": employee_second.id,
                "company_id": company.id,
                "payslip_run_id": cls.payslip_run.id,
                "move_id": cls.move_second.id,
                "date_from": cls.payslip_run.date_start,
                "date_to": cls.payslip_run.date_end,
            }
        )

    def test_action_creates_payment_order_and_populates_wizard(self):
        """Batch action must create a payment order and
        pre-load move lines from the batch into the wizard."""
        action = self.payslip_run.action_open_payment_order_wizard()
        ctx = action.get("context", {})
        self.assertEqual(
            ctx.get("active_model"),
            "account.payment.order",
            "active_model should be account.payment.order",
        )
        payment_order = self.env["account.payment.order"].browse(ctx["active_id"])
        self.assertTrue(payment_order.exists(), "Payment order was not created")
        self.assertEqual(payment_order.payment_mode_id, self.payment_mode)

        wizard = self.env["account.payment.line.create"].with_context(**ctx).create({})
        self.assertEqual(
            wizard.payslip_run_id,
            self.payslip_run,
            "Wizard should be linked to the payslip batch",
        )

        payable_lines = (self.move.line_ids + self.move_second.line_ids).filtered(
            lambda line: line.account_id == self.payment_account
        )
        self.assertEqual(
            len(payable_lines),
            2,
            "Test setup should have two payroll payable move lines in the batch",
        )
        for line in payable_lines:
            self.assertIn(
                line,
                wizard.move_line_ids,
                "Wizard did not load all expected payable move lines from batch",
            )

    def test_action_raises_error_when_no_payslips(self):
        """Button must raise a clear error if the batch has no payslips."""
        empty_run = self.env["hr.payslip.run"].create(
            {
                "name": "Empty Payroll Batch",
                "date_start": fields.Date.today().replace(day=1),
                "date_end": fields.Date.today(),
                "company_id": self.env.company.id,
            }
        )
        with self.assertRaises(UserError):
            empty_run.action_open_payment_order_wizard()

    def test_action_uses_fallback_payment_mode_when_field_is_empty(self):
        """If payment_mode_id is not set, method must fallback to a valid mode."""
        self.payslip_run.payment_mode_id = False
        action = self.payslip_run.action_open_payment_order_wizard()
        ctx = action.get("context", {})
        order = self.env["account.payment.order"].browse(ctx["active_id"])
        self.assertTrue(order.payment_mode_id)
        self.assertEqual(order.payment_mode_id.payment_type, "outbound")

    def test_wizard_respects_payment_account_filter(self):
        """Wizard must restrict lines to the batch payment account if set."""
        other_account = self.env["account.account"].create(
            {
                "name": "Other Payable (Test)",
                "code": "TST99902",
                "account_type": "liability_payable",
                "reconcile": True,
                "company_id": self.env.company.id,
            }
        )
        self.payslip_run.payment_account_id = other_account

        action = self.payslip_run.action_open_payment_order_wizard()
        ctx = action.get("context", {})
        wizard = self.env["account.payment.line.create"].with_context(**ctx).create({})
        self.assertFalse(
            wizard.move_line_ids,
            "Wizard should not load move lines when payment account "
            "does not match any batch lines",
        )
