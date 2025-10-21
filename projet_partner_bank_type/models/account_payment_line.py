# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    @api.onchange("partner_id", "move_line_id")
    def partner_id_change(self):
        res = super().partner_id_change()

        partner_bank = False
        journal = self.move_line_id.move_id.journal_id if self.move_line_id else False
        journal_usage = journal.journal_usage if journal else False

        if journal_usage and self.partner_id:
            partner_bank = self.partner_id.bank_ids.filtered(
                lambda b, usage=journal_usage: b.bank_account_usage == usage
            )[:1]

        if partner_bank:
            self.partner_bank_id = partner_bank.id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move_line = (
                self.env["account.move.line"].browse(vals["move_line_id"])
                if vals.get("move_line_id")
                else False
            )

            journal = move_line.move_id.journal_id if move_line else False
            journal_usage = journal.journal_usage if journal else False
            partner = (
                self.env["res.partner"].browse(vals["partner_id"])
                if vals.get("partner_id")
                else (move_line.partner_id if move_line else False)
            )

            if not (journal_usage and partner):
                continue
            partner_bank = partner.bank_ids.filtered(
                lambda b, usage=journal_usage: b.bank_account_usage == usage
            )[:1]

            if partner_bank:
                vals["partner_bank_id"] = partner_bank.id
        return super().create(vals_list)
