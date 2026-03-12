# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSupplierContractTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref(
            "project_supplier_contract_report.supplier_contract_template_default"
        )
        cls.report_view = cls.env.ref(
            "project_supplier_contract_report.report_supplier_contract"
        )

    def test_default_template_data(self):
        self.assertTrue(self.template)
        self.assertEqual(self.template.name, "Default Supplier Contract")
        self.assertEqual(self.template.report_template_id, self.report_view)
        self.assertTrue(self.template.active)

    def test_create_template(self):
        new_template = self.env["supplier.contract.report.template"].create(
            {
                "name": "Template Test",
                "report_template_id": self.report_view.id,
                "active": True,
            }
        )
        self.assertTrue(new_template)
        self.assertEqual(new_template.report_template_id, self.report_view)
