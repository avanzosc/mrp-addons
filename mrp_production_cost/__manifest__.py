# Copyright 2022 Patxi lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Production Cost",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "version": "18.0.1.0.0",
    "depends": [
        "product",
        "mrp",
        "stock",
        "stock_move_cost",
        "product_cost_security_read_permission",
    ],
    "data": [
        "views/mrp_production_views.xml",
        "views/mrp_stockmove_views.xml",
        "views/mrp_workorder_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_production_cost/static/src/js/mrp_bom_overview.esm.js",
        ],
    },
    "installable": True,
    "pre_init_hook": "_pre_init_mrp_production_cost",
    "post_init_hook": "_post_init_mrp_production_cost",
}
