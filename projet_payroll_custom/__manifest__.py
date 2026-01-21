# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Projet Payroll Custom",
    "summary": "Integra lote de holerites com Ordens de Pagamento",
    "version": "16.0.1.0.0",
    "author": "Escodoo",
    "license": "AGPL-3",
    "website": "https://github.com/Escodoo/projet-addons",
    "depends": [
        "payroll",
        "payroll_account",
        "account_payment_order",
    ],
    "data": [
        "views/hr_payslip_run_views.xml",
        "views/account_payment_line_create_views.xml",
    ],
    "demo": [
        "demo/payroll_payment_order_demo.xml",
    ],
    "installable": True,
}
