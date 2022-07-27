# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Custom MRP Line Cost",
    "version": "14.0.1.0.0",
    "category": "MRP",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "mrp",
        "mrp_bom_line_coef",
        "mrp_production_deconstruction",
        "custom_breeding_apps"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mrp_standar_price_decimal_precision.xml",
        "data/mrp_killing_cost.xml",
        "views/mrp_production_view.xml",
        "views/product_template_view.xml",
        "views/killing_cost_view.xml",
    ],
    "installable": True,
}
