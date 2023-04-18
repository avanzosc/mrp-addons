# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp BoM Line Semi Finished",
    "version": "14.0.1.0.0",
    "category": "MRP",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "product",
        "sale",
        "stock",
        "mrp",
        "uom"
    ],
    "data": [
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "views/mrp_bom_views.xml",
        "views/mrp_bom_line_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
