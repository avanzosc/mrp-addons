# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Line MRP Link",
    "version": "14.0.1.0.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "sale_order_line_menu",
        "sale_mrp",
        "stock"
    ],
    "data": [
        "views/mrp_production_views.xml",
        "views/sale_order_line_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
