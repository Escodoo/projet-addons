# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    signed_document_ids = fields.One2many(
        string="Signed Documents",
        comodel_name="hr.contract.signed.document",
        inverse_name="contract_id",
    )
