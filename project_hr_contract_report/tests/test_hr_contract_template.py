# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestHrContractTemplate(TransactionCase):
    """Test cases for hr.contract.template model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.default_view = cls.env.ref(
            "project_hr_contract_report.report_hr_contract_br"
        )

        cls.default_report = cls.env.ref(
            "project_hr_contract_report.action_report_hr_contract_br"
        )

        cls.template = cls.env["hr.contract.template"].create(
            {
                "name": "Test Template",
                "report_template_id": cls.default_view.id,
                "description": "Test template description",
                "active": True,
            }
        )

    def test_template_creation(self):
        """Test template creation"""
        self.assertTrue(self.template)
        self.assertEqual(self.template.name, "Test Template")
        self.assertEqual(self.template.report_template_id, self.default_view)
        self.assertTrue(self.template.active)

    def test_template_duplicate(self):
        """Test template duplication"""
        # Duplicate the template
        result = self.template.action_duplicate()

        # Check that result is a dict (action window)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "hr.contract.template")

        # Get the duplicated template
        new_template_id = result["res_id"]
        new_template = self.env["hr.contract.template"].browse(new_template_id)

        # Check that template was duplicated
        self.assertTrue(new_template)
        self.assertEqual(new_template.name, f"{self.template.name} (Copy)")
        self.assertNotEqual(new_template.id, self.template.id)

        # Check that view was duplicated
        new_view = new_template.report_template_id
        self.assertTrue(new_view)
        self.assertNotEqual(new_view.id, self.default_view.id)
        self.assertIn("_copy_", new_view.key)

        # Check that report was duplicated
        new_report = self.env["ir.actions.report"].search(
            [("report_name", "=", new_view.key)], limit=1
        )
        self.assertTrue(new_report)
        self.assertNotEqual(new_report.id, self.default_report.id)

        # Check that external IDs were created
        view_xmlid = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", new_view.id)], limit=1
        )
        self.assertTrue(view_xmlid)
        self.assertTrue(view_xmlid.noupdate)

        report_xmlid = self.env["ir.model.data"].search(
            [("model", "=", "ir.actions.report"), ("res_id", "=", new_report.id)],
            limit=1,
        )
        self.assertTrue(report_xmlid)
        self.assertTrue(report_xmlid.noupdate)

    def test_template_duplicate_no_report(self):
        """Test template duplication when report action doesn't exist"""
        # Create a view without a corresponding report
        new_view = self.default_view.copy(
            {
                "key": "project_hr_contract_report.test_view_no_report",
            }
        )

        # Create external ID for the view
        self.env["ir.model.data"].create(
            {
                "module": "project_hr_contract_report",
                "name": "test_view_no_report",
                "model": "ir.ui.view",
                "res_id": new_view.id,
            }
        )

        # Create template with this view
        template_no_report = self.env["hr.contract.template"].create(
            {
                "name": "Template Without Report",
                "report_template_id": new_view.id,
            }
        )

        # Try to duplicate - should raise error
        with self.assertRaises(UserError):
            template_no_report.action_duplicate()

    def test_template_active_toggle(self):
        """Test template active field toggle"""
        self.assertTrue(self.template.active)

        # Deactivate
        self.template.active = False
        self.assertFalse(self.template.active)

        # Activate
        self.template.active = True
        self.assertTrue(self.template.active)
