# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrContractTemplateWizard(models.TransientModel):
    _name = "hr.contract.template.wizard"
    _description = "Contract Template Selection Wizard"

    contract_id = fields.Many2one(
        string="Contract",
        comodel_name="hr.contract",
        required=True,
    )
    template_id = fields.Many2one(
        string="Template",
        comodel_name="hr.contract.template",
        required=True,
        domain=[("active", "=", True)],
    )

    @api.model
    def default_get(self, fields_list):
        """Set first active template as default if available"""
        res = super().default_get(fields_list)
        if "template_id" in fields_list:
            first_template = self.env["hr.contract.template"].search(
                [("active", "=", True)], limit=1, order="id"
            )
            if first_template:
                res["template_id"] = first_template.id
        return res

    def action_print(self):
        """Print contract using selected template"""
        self.ensure_one()
        if not self.template_id.report_template_id:
            return False

        # Get the template key (external ID of the view)
        template_key = self.template_id.report_template_id.key

        # Get the base report action
        base_report = self.env["ir.actions.report"].search(
            [
                ("model", "=", "hr.contract"),
                (
                    "report_name",
                    "=",
                    "project_hr_contract_report.report_hr_contract_br",
                ),
            ],
            limit=1,
        )

        if not base_report:
            return False

        # Create a temporary report action pointing to the selected view
        temp_report = self.env["ir.actions.report"].create(
            {
                "name": f"{base_report.name} - {self.template_id.name}",
                "model": "hr.contract",
                "report_type": "qweb-pdf",
                "report_name": template_key,  # This is the key of the QWeb view
                "print_report_name": base_report.print_report_name
                or "'Contract - %s' % (object.name or 'Sem referência')",
            }
        )

        try:
            # Print using the temporary report
            result = temp_report.report_action(self.contract_id)
            return result
        finally:
            # Clean up temporary report
            temp_report.unlink()
