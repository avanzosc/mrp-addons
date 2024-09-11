# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Custom MRP Line Cost",
    "version": "14.0.1.1.0",
    "category": "MRP",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
        "mrp_bom_line_coef",
        "mrp_production_deconstruction",
        "stock_move_line_cost",
        "custom_descarga",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mrp_standar_price_decimal_precision.xml",
        "views/mrp_production_view.xml",
        "views/product_template_view.xml",
        "views/killing_cost_view.xml",
        "views/mrp_bom_view.xml",
        "views/stock_move_line_view.xml",
        "views/mrp_workcenter_view.xml",
        "views/mrp_workorder_view.xml",
        "views/mrp_routing_workcenter_view.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
