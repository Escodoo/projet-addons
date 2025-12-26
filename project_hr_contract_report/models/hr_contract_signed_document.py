# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrContractSignedDocument(models.Model):
    _name = "hr.contract.signed.document"
    _description = "Signed Contract Document"
    _order = "create_date desc"

    name = fields.Char(string="Document Name", required=True)
    contract_id = fields.Many2one(
        string="Contract",
        comodel_name="hr.contract",
        required=True,
        ondelete="cascade",
    )
    template_id = fields.Many2one(
        string="Template Used",
        comodel_name="hr.contract.template",
        required=True,
        help="Template that was used to generate this signed document",
    )
    attachment = fields.Binary(
        string="Signed Document",
        required=True,
        help="The signed contract document file",
    )
    attachment_filename = fields.Char(string="Filename")
    date_signed = fields.Date(
        default=fields.Date.today,
        help="Date when the contract was signed",
    )
    notes = fields.Text()

    @api.model
    def default_get(self, fields_list):
        """Set default name based on template"""
        res = super().default_get(fields_list)
        if "name" in fields_list and not res.get("name"):
            if res.get("template_id"):
                template = self.env["hr.contract.template"].browse(res["template_id"])
                res["name"] = template.name
        return res

    @api.onchange("template_id")
    def _onchange_template_id(self):
        """Update name when template changes"""
        if self.template_id:
            self.name = self.template_id.name
