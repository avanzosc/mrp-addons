# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Product Version Stock",
    "version": "12.0.1.0.2",
    "license": "AGPL-3",
    "depends": [
        "product_variant_custom",
        "stock",
        "sale",
        "purchase",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "",
    "data": [
        "security/ir.model.access.csv",
        "views/stock_production_lot_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_inventory_product_version_graph.xml",
        "views/product_view.xml",
        "views/stock_view.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
