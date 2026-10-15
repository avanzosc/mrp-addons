# Copyright 2022 Patxi lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Production Cost",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "MRP",
    "license": "AGPL-3",
    "version": "14.0.1.1.0",
    "depends": ["product", "mrp", "stock", "stock_move_cost", "product_cost_security"],
    "data": [
        "views/mrp_production_views.xml",
        "views/mrp_stockmove_views.xml",
        "views/mrp_workorder_views.xml",
        "report/mrp_bom_report.xml",
    ],
    "installable": True,
    "auto_install": True,
    "pre_init_hook": "_pre_init_mrp_production_cost",
    "post_init_hook": "_post_init_mrp_production_cost",
}
