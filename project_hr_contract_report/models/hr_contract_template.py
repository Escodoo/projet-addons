# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

from odoo import _, fields, models
from odoo.exceptions import UserError


class HrContractTemplate(models.Model):
    _name = "hr.contract.template"
    _description = "Contract Template"
    _order = "name"

    name = fields.Char(string="Template Name", required=True)
    active = fields.Boolean(default=True)
    report_template_id = fields.Many2one(
        string="Report Template",
        comodel_name="ir.ui.view",
        domain=[("type", "=", "qweb"), ("key", "like", "project_hr_contract_report%")],
        required=True,
        ondelete="restrict",
    )
    description = fields.Text()

    def action_duplicate(self):
        self.ensure_one()

        original_view = self.report_template_id
        if not original_view:
            raise UserError(_("No report template associated with this template."))
        original_report = self.env["ir.actions.report"].search(
            [("report_name", "=", original_view.key)], limit=1
        )
        if not original_report:
            raise UserError(_("Original report action not found for this template."))

        timestamp = int(time.time())
        xmlid = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", original_view.id)],
            limit=1,
        )

        if xmlid:
            module = xmlid.module
            base_name = xmlid.name
        else:
            module = "project_hr_contract_report"
            base_name = original_view.key.split(".")[-1]

        new_base_name = f"{base_name}_copy_{timestamp}"
        new_view_key = f"{module}.{new_base_name}"
        new_view = original_view.copy(
            {
                "name": f"{original_view.name} (Copy)",
                "key": new_view_key,
                "model": original_view.model or "hr.contract",
            }
        )

        # Create external ID for the new view
        self.env["ir.model.data"].create(
            {
                "module": module,
                "name": new_base_name,
                "model": "ir.ui.view",
                "res_id": new_view.id,
                "noupdate": True,
            }
        )
        new_report = original_report.copy(
            {
                "name": f"{original_report.name} (Copy)",
                "report_name": new_view.key,
                "report_file": new_view.key,
            }
        )

        self.env["ir.model.data"].create(
            {
                "module": module,
                "name": f"{new_base_name}_report",
                "model": "ir.actions.report",
                "res_id": new_report.id,
                "noupdate": True,
            }
        )
        new_template = self.copy(
            {
                "name": f"{self.name} (Copy)",
                "report_template_id": new_view.id,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Contract Template"),
            "res_model": "hr.contract.template",
            "res_id": new_template.id,
            "view_mode": "form",
            "target": "current",
        }
