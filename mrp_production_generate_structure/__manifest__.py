# Copyright 2018 Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Production Generate Structure",
    "version": "12.0.1.3.2",
    "license": "AGPL-3",
    "author": "AvanzOSC, ",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "depends": [
        "mrp_scheduled_products",
        "purchase_stock",
        "mrp_analytic"
    ],
    "data": [
        "views/mrp_production_product_line_view.xml",
        "views/mrp_production_view.xml",
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
