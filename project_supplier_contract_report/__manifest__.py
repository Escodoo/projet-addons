# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Supplier Contract Report",
    "summary": "Supplier contract report with selectable QWeb templates",
    "version": "16.0.1.0.0",
    "author": "Escodoo",
    "license": "AGPL-3",
    "website": "https://github.com/Escodoo/projet-addons",
    "depends": [
        "contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/report_templates.xml",
        "data/report_action.xml",
        "data/supplier_contract_template_data.xml",
        "views/contract_views.xml",
    ],
    "maintainers": ["CristianoMafraJunior"],
    "installable": True,
}
