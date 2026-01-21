# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode",
        domain=[
            ("payment_order_ok", "=", True),
            ("payment_type", "=", "outbound"),
        ],
    )
    payment_account_id = fields.Many2one(
        "account.account",
        string="Payment Account",
        domain=[("reconcile", "=", True)],
    )
    payment_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Payment Analytic Account",
    )

    def action_open_payment_order_wizard(self):
        self.ensure_one()
        if not self.slip_ids:
            raise UserError(_("There are no payslips in this batch."))

        company = self.company_id
        payment_mode = self.payment_mode_id
        if not payment_mode:
            payment_mode = self.env["account.payment.mode"].search(
                [
                    ("payment_order_ok", "=", True),
                    ("payment_type", "=", "outbound"),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
        if not payment_mode:
            raise UserError(
                _(
                    "No outbound payment mode configured for payment orders "
                    "in company %s."
                )
                % company.display_name
            )

        payment_order = self.env["account.payment.order"].create(
            {
                "payment_mode_id": payment_mode.id,
                "description": self.name,
            }
        )

        action = self.env.ref(
            "account_payment_order.account_payment_line_create_action"
        ).read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "active_model": "account.payment.order",
                "active_id": payment_order.id,
                "default_order_id": payment_order.id,
                "payslip_run_id": self.id,
                "default_payslip_run_id": self.id,
                "auto_populate_from_payslip_run": True,
            }
        )
        action["context"] = ctx
        return action
