# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    payslip_run_id = fields.Many2one(
        "hr.payslip.run",
        string="Payslip Batch",
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        ctx = self.env.context
        payslip_run_id = ctx.get("payslip_run_id") or ctx.get("default_payslip_run_id")
        if payslip_run_id:
            res.setdefault("payslip_run_id", payslip_run_id)
        if ctx.get("auto_populate_from_payslip_run"):
            payslip_run = self.env["hr.payslip.run"].browse(payslip_run_id)
            order = None
            if ctx.get("active_model") == "account.payment.order" and ctx.get(
                "active_id"
            ):
                order = self.env["account.payment.order"].browse(ctx["active_id"])
            if payslip_run and order:
                payment_account = payslip_run.payment_account_id
                payment_analytic = payslip_run.payment_analytic_account_id
                moves = payslip_run.slip_ids.mapped("move_id").filtered(
                    lambda m: m.state == "posted"
                )
                if moves:
                    domain = [
                        ("move_id", "in", moves.ids),
                        ("company_id", "=", order.company_id.id),
                        ("reconciled", "=", False),
                        ("account_id.reconcile", "=", True),
                    ]
                    if payment_account:
                        domain.append(("account_id", "=", payment_account.id))
                    if payment_analytic:
                        domain.append(
                            ("analytic_line_ids.account_id", "=", payment_analytic.id)
                        )
                    lines = self.env["account.move.line"].search(domain)
                    res["move_line_ids"] = [(6, 0, lines.ids)]
        return res

    def _prepare_move_line_domain(self):
        domain = super()._prepare_move_line_domain()
        if self.payslip_run_id:
            moves = self.payslip_run_id.slip_ids.mapped("move_id").filtered(
                lambda m: m.state == "posted"
            )
            if moves:
                domain.append(("move_id", "in", moves.ids))
            else:
                domain.append(("id", "=", 0))
        return domain
