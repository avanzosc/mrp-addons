# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Quality Control Test Method",
    'version': '14.0.1.0.0',
    "author": "Avanzosc",
    "website": "https://www.avanzosc.es",
    "category": "MRP",
    "depends": [
        "quality_control_oca",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/qc_test_views.xml",
        "views/qc_test_method_views.xml",
        "views/qc_test_proof_views.xml",
        "views/qc_inspection_line_views.xml",
        "views/qc_test_question_views.xml",
        "views/qc_inspection_views.xml"
    ],
    "license": "AGPL-3",
    'installable': True,
}
