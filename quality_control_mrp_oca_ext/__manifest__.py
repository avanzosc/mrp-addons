# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Quality Control Mrp Oca Ext",
    "version": "16.0.1.0.0",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Quality control",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    "license": "AGPL-3",
    "depends": [
        "quality_control_stock_oca",
        "quality_control_mrp_oca",
        "mrp_production_initial_quality_control",
        "qc_inspection_mrp_report",
    ],
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "reports/qc_inspection_report.xml",
        "views/extended_quality_control_verification_type_view.xml",
        "views/extended_quality_control_packaging_view.xml",
        "views/extended_quality_control_component_view.xml",
        "views/extended_quality_control_solution_view.xml",
        "views/extended_quality_control_line_view.xml",
        "views/extended_quality_control_view.xml",
        "views/product_template_view.xml",
        "views/mrp_production_view.xml",
        "views/qc_test_view.xml",
        "views/qc_test_question_view.xml",
        "views/qc_inspection_type_view.xml",
        "views/qc_inspection_view.xml",
        "views/stock_move_view.xml",
    ],
    "installable": True,
}
