# Copyright 2018 Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Production Generate Structure",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC, ",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "depends": [
        "mrp_production_editable_scheduled_products",
        "purchase",
    ],
    "data": [
        "views/mrp_production_product_line_view.xml",
        "views/mrp_production_view.xml",
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
