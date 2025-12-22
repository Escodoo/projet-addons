# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrContractTemplateWizard(TransactionCase):
    """Test cases for hr.contract.template.wizard model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env["res.company"].create(
            {
                "name": "Test Company",
            }
        )

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "company_id": cls.company.id,
            }
        )

        cls.template = cls.env.ref(
            "project_hr_contract_report.hr_contract_template_default"
        )

        cls.contract = cls.env["hr.contract"].create(
            {
                "name": "Test Contract",
                "employee_id": cls.employee.id,
                "company_id": cls.company.id,
                "date_start": "2025-01-01",
                "wage": 5000.0,
            }
        )

    def test_wizard_creation(self):
        """Test wizard creation"""
        wizard = self.env["hr.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )

        self.assertTrue(wizard)
        self.assertEqual(wizard.contract_id, self.contract)
        self.assertEqual(wizard.template_id, self.template)

    def test_wizard_default_get(self):
        """Test wizard default_get sets first active template"""
        # Create another active template
        view = self.template.report_template_id
        self.env["hr.contract.template"].create(
            {
                "name": "Template 2",
                "report_template_id": view.id,
                "active": True,
            }
        )

        # Get defaults
        defaults = self.env["hr.contract.template.wizard"].default_get(["template_id"])

        # Should have a template (first active one)
        self.assertIn("template_id", defaults)
        self.assertTrue(defaults["template_id"])

    def test_wizard_action_print(self):
        """Test wizard action_print"""
        wizard = self.env["hr.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )

        # Call action_print
        result = wizard.action_print()

        # Should return a dict with action
        self.assertIsInstance(result, dict)
        self.assertIn("type", result)

        # Check that temporary report was cleaned up
        temp_reports = self.env["ir.actions.report"].search(
            [
                ("name", "like", f"%{self.template.name}%"),
            ]
        )
        # Should be empty or only the base report
        self.assertLessEqual(len(temp_reports), 1)

    def test_wizard_action_print_no_template_view(self):
        """Test wizard action_print when template has no view"""
        # Create a new template with view first
        view = self.template.report_template_id
        template_test = self.env["hr.contract.template"].create(
            {
                "name": "Test Template No View",
                "report_template_id": view.id,
            }
        )

        # Temporarily remove view (this simulates the error condition)
        template_test.report_template_id = False

        wizard = self.env["hr.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": template_test.id,
            }
        )

        # Should return False
        result = wizard.action_print()
        self.assertFalse(result)

    def test_wizard_action_print_no_base_report(self):
        """Test wizard action_print when base report doesn't exist"""
        wizard = self.env["hr.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )

        # Delete base report
        base_report = self.env["ir.actions.report"].search(
            [
                (
                    "report_name",
                    "=",
                    "project_hr_contract_report.report_hr_contract_br",
                ),
            ],
            limit=1,
        )
        if base_report:
            base_report.unlink()

        # Should return False
        result = wizard.action_print()
        self.assertFalse(result)
