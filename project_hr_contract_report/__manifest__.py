# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "HR Contract Report with Template Selection",
    "summary": """Employment Contract Report with Template
        Selection and Signed Documents""",
    "version": "16.0.1.0.0",
    "author": "Escodoo",
    "license": "AGPL-3",
    "website": "https://github.com/Escodoo/projet-addons",
    "depends": [
        "hr",
        "l10n_br_hr_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/report_templates.xml",
        "data/report_action.xml",
        "data/hr_contract_template_data.xml",
        "views/hr_contract_views.xml",
    ],
    "installable": True,
}
