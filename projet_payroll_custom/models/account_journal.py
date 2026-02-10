# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    payslip_run_payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode (Payslip Batch)",
        domain="["
        "('payment_order_ok', '=', True), "
        "('payment_type', '=', 'outbound'), "
        "('company_id', '=', company_id)"
        "]",
    )
    payslip_run_payment_account_id = fields.Many2one(
        "account.account",
        string="Payment Account (Payslip Batch)",
    )
    payslip_run_payment_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Payment Analytic Account (Payslip Batch)",
    )
