# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import fields
from odoo.tests.common import TransactionCase


class TestHrContractSignedDocument(TransactionCase):
    """Test cases for hr.contract.signed.document model"""

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
                "date_start": fields.Date.today(),
                "wage": 5000.0,
            }
        )

    def test_signed_document_creation(self):
        content = base64.b64encode(b"test file content").decode("utf-8")
        document = self.env["hr.contract.signed.document"].create(
            {
                "name": "Test Document",
                "contract_id": self.contract.id,
                "template_id": self.template.id,
                "attachment": content,
                "attachment_filename": "test.pdf",
                "date_signed": fields.Date.today(),
            }
        )
        self.assertTrue(document)
        self.assertEqual(document.name, "Test Document")
        self.assertEqual(document.contract_id, self.contract)
        self.assertEqual(document.template_id, self.template)
        self.assertEqual(document.attachment_filename, "test.pdf")

    def test_signed_document_default_name_from_template(self):
        document = self.env["hr.contract.signed.document"].new(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )
        defaults = document.default_get(["name", "template_id"])
        if defaults.get("template_id"):
            template = self.env["hr.contract.template"].browse(defaults["template_id"])
            if "name" in defaults:
                self.assertEqual(defaults["name"], template.name)

    def test_signed_document_onchange_template(self):
        document = self.env["hr.contract.signed.document"].new(
            {
                "contract_id": self.contract.id,
                "name": "Old Name",
            }
        )
        document.template_id = self.template
        document._onchange_template_id()
        self.assertEqual(document.name, self.template.name)

    def test_signed_document_cascade_delete(self):
        content = base64.b64encode(b"test file content").decode("utf-8")

        document = self.env["hr.contract.signed.document"].create(
            {
                "name": "Test Document",
                "contract_id": self.contract.id,
                "template_id": self.template.id,
                "attachment": content,
                "attachment_filename": "test.pdf",
            }
        )

        document_id = document.id
        self.contract.unlink()

        self.assertFalse(
            self.env["hr.contract.signed.document"].browse(document_id).exists()
        )

    def test_signed_document_date_default(self):
        document = self.env["hr.contract.signed.document"].new(
            {
                "contract_id": self.contract.id,
                "template_id": self.template.id,
            }
        )

        self.assertEqual(document.date_signed, fields.Date.today())
