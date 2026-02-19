# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SupplierContractTemplateWizard(models.TransientModel):
    _name = "supplier.contract.template.wizard"
    _description = "Supplier Contract Template Selection Wizard"

    contract_id = fields.Many2one(
        string="Contract",
        comodel_name="contract.contract",
        required=True,
    )
    template_id = fields.Many2one(
        string="Template",
        comodel_name="supplier.contract.report.template",
        required=True,
        domain=[("active", "=", True)],
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "contract_id" in fields_list and not res.get("contract_id"):
            contract_id = self.env.context.get(
                "default_contract_id"
            ) or self.env.context.get("active_id")
            if contract_id:
                res["contract_id"] = contract_id
        if "template_id" in fields_list:
            first_template = self.env["supplier.contract.report.template"].search(
                [("active", "=", True)],
                limit=1,
                order="id",
            )
            if first_template:
                res["template_id"] = first_template.id
        return res

    def action_print(self):
        self.ensure_one()
        if not self.template_id.report_template_id:
            return False

        template_key = self.template_id.report_template_id.key
        base_report = self.env["ir.actions.report"].search(
            [
                ("model", "=", "contract.contract"),
                (
                    "report_name",
                    "=",
                    "project_supplier_contract_report.report_supplier_contract",
                ),
            ],
            limit=1,
        )
        if not base_report:
            return False

        temp_report = self.env["ir.actions.report"].create(
            {
                "name": f"{base_report.name} - {self.template_id.name}",
                "model": "contract.contract",
                "report_type": "qweb-pdf",
                "report_name": template_key,
                "print_report_name": base_report.print_report_name
                or "'Supplier Contract - %s' % (object.name or 'No Reference')",
            }
        )
        try:
            return temp_report.with_context(discard_logo_check=True).report_action(
                self.contract_id
            )
        finally:
            temp_report.unlink()
