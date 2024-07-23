# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Production Stencil Product",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "stock",
        "product",
        "uom",
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/mrp_production_report.xml",
        "views/mrp_bom_views.xml",
        "views/mrp_production_views.xml",
        "views/mrp_workorder_views.xml",
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
    ],
    "installable": True,
}
