# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Order Manufacturing Order Inspection",
    "version": "14.0.1.0.0",
    "category": "Sales/Sales",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "sale",
        "quality_control_oca",
        "quality_control_mrp_oca",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/mrp_production_views.xml",
        "views/qc_test_views.xml",
        "views/qc_test_label_views.xml",
    ],
    "installable": True,
}
