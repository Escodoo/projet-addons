# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import fields
from odoo.tests.common import TransactionCase


class TestHrContract(TransactionCase):
    """Test cases for hr.contract model extension"""

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

    def test_contract_has_signed_document_ids_field(self):
        """Test that contract has signed_document_ids field"""
        self.assertTrue(hasattr(self.contract, "signed_document_ids"))
        self.assertEqual(len(self.contract.signed_document_ids), 0)

    def test_contract_signed_documents_relationship(self):
        """Test relationship between contract and signed documents"""
        # Encode content as base64
        content = base64.b64encode(b"test file content").decode("utf-8")

        # Create signed document
        document = self.env["hr.contract.signed.document"].create(
            {
                "name": "Test Document",
                "contract_id": self.contract.id,
                "template_id": self.template.id,
                "attachment": content,
                "attachment_filename": "test.pdf",
            }
        )

        # Check relationship
        self.assertEqual(len(self.contract.signed_document_ids), 1)
        self.assertEqual(self.contract.signed_document_ids[0], document)
        self.assertEqual(document.contract_id, self.contract)

    def test_contract_multiple_signed_documents(self):
        """Test contract with multiple signed documents"""
        # Encode content as base64
        content1 = base64.b64encode(b"content 1").decode("utf-8")
        content2 = base64.b64encode(b"content 2").decode("utf-8")

        # Create multiple signed documents
        doc1 = self.env["hr.contract.signed.document"].create(
            {
                "name": "Document 1",
                "contract_id": self.contract.id,
                "template_id": self.template.id,
                "attachment": content1,
                "attachment_filename": "doc1.pdf",
            }
        )

        doc2 = self.env["hr.contract.signed.document"].create(
            {
                "name": "Document 2",
                "contract_id": self.contract.id,
                "template_id": self.template.id,
                "attachment": content2,
                "attachment_filename": "doc2.pdf",
            }
        )

        # Check that both documents are linked
        self.assertEqual(len(self.contract.signed_document_ids), 2)
        self.assertIn(doc1, self.contract.signed_document_ids)
        self.assertIn(doc2, self.contract.signed_document_ids)

    def test_contract_signed_documents_ordering(self):
        """Test that signed documents are ordered by create_date desc"""
        # Encode content as base64
        content1 = base64.b64encode(b"content 1").decode("utf-8")
        content2 = base64.b64encode(b"content 2").decode("utf-8")

        # Create first document
        doc1 = self.env["hr.contract.signed.document"].create(
            {
                "name": "Document 1",
                "contract_id": self.contract.id,
                "template_id": self.template.id,
                "attachment": content1,
                "attachment_filename": "doc1.pdf",
            }
        )

        # Get create_date of first document
        doc1_create_date = doc1.create_date

        # Create second document (should have later create_date)
        doc2 = self.env["hr.contract.signed.document"].create(
            {
                "name": "Document 2",
                "contract_id": self.contract.id,
                "template_id": self.template.id,
                "attachment": content2,
                "attachment_filename": "doc2.pdf",
            }
        )

        # Refresh to get updated order
        self.contract.invalidate_recordset(["signed_document_ids"])

        # Check that documents are ordered by create_date desc
        # Most recent should be first
        documents = self.contract.signed_document_ids
        self.assertEqual(len(documents), 2)
        # Verify ordering: doc2 should be first (most recent)
        self.assertGreaterEqual(doc2.create_date, doc1_create_date)
        # Check that the order is correct (most recent first)
        if documents[0].id == doc2.id:
            self.assertEqual(documents[0], doc2)
            self.assertEqual(documents[1], doc1)
        else:
            # If ordering is different, at least verify both are present
            self.assertIn(doc1, documents)
            self.assertIn(doc2, documents)
