# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Projet Partner Bank Type",
    "summary": """This module adds a field in res.partner.bank to
    classify accounts as Expense or Salary type and also
    select the correct account in account.payment.line
    based on the journal""",
    "version": "16.0.1.0.0",
    "author": "Escodoo",
    "license": "AGPL-3",
    "website": "https://github.com/Escodoo/projet-addons",
    "depends": [
        "l10n_br_base",
        "l10n_br_account_payment_order",
    ],
    "data": [
        "views/res_partner_bank_view.xml",
        "views/account_journal_view.xml",
    ],
    "installable": True,
}
