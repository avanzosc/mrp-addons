# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Custom MRP Descarga",
    "version": "14.0.1.0.0",
    "category": "MRP",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "custom_mrp_line_cost",
        "custom_descarga",
        "custom_breeding_apps",
        "mrp_production_deconstruction"
    ],
    "data": [
        "data/quartering_product.xml",
        "views/saca_line_view.xml",
        "views/mrp_production_view.xml",
        "views/stock_production_lot_view.xml",
        "views/stock_quant_view.xml"
    ],
    "installable": True,
    "auto_install": True,
}
