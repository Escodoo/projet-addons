# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSupplierContractTemplateWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test Pricelist"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
                "property_product_pricelist": cls.pricelist.id,
                "supplier_rank": 1,
            }
        )
        cls.template = cls.env.ref(
            "project_supplier_contract_report.supplier_contract_template_default"
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Supplier Contract",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "line_recurrence": True,
                "contract_type": "purchase",
            }
        )

    def test_wizard_creation(self):
        wizard = self.env["supplier.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )
        self.assertTrue(wizard)
        self.assertEqual(wizard.contract_id, self.contract)
        self.assertEqual(wizard.template_id, self.template)

    def test_wizard_default_get(self):
        defaults = (
            self.env["supplier.contract.template.wizard"]
            .with_context(default_contract_id=self.contract.id)
            .default_get(["contract_id", "template_id"])
        )
        self.assertEqual(defaults.get("contract_id"), self.contract.id)
        self.assertTrue(defaults.get("template_id"))

    def test_wizard_action_print(self):
        wizard = self.env["supplier.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )
        result = wizard.action_print()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("type"), "ir.actions.report")

        temp_reports = self.env["ir.actions.report"].search(
            [("name", "like", f"%{self.template.name}%")]
        )
        self.assertFalse(temp_reports)

    def test_wizard_action_print_no_template_view(self):
        self.template.report_template_id = False
        wizard = self.env["supplier.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )
        result = wizard.action_print()
        self.assertFalse(result)

    def test_wizard_action_print_no_base_report(self):
        base_report = self.env["ir.actions.report"].search(
            [
                (
                    "report_name",
                    "=",
                    "project_supplier_contract_report.report_supplier_contract",
                )
            ],
            limit=1,
        )
        if base_report:
            base_report.unlink()

        wizard = self.env["supplier.contract.template.wizard"].create(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )
        result = wizard.action_print()
        self.assertFalse(result)
