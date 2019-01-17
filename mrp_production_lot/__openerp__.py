# -*- coding: utf-8 -*-
# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Production Lot",
    "version": "8.0.1.0.0",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "category": "Custom module",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    "depends": [
        "mrp",
        "product_expiry_ext"
        ],
    "data": [
        "wizard/mrp_product_produce_view.xml",
        "views/mrp_production_view.xml",
        "views/stock_production_lot_view.xml",
        ],
    "installable": True
}
