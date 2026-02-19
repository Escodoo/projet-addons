# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SupplierContractReportTemplate(models.Model):
    _name = "supplier.contract.report.template"
    _description = "Supplier Contract Report Template"
    _order = "name"

    name = fields.Char(string="Template Name", required=True)
    active = fields.Boolean(default=True)
    report_template_id = fields.Many2one(
        string="Report Template",
        comodel_name="ir.ui.view",
        domain=[
            ("type", "=", "qweb"),
            ("key", "like", "project_supplier_contract_report%"),
        ],
        required=True,
        ondelete="restrict",
    )
    description = fields.Text()
