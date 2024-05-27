# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Aggregate/create purchase lines",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "sale_order_line_input",
        "mrp_production_generate_structure",
    ],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Tools",
    "data": [
        "views/sale_order_line_view.xml",
        "views/purchase_order_line_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
