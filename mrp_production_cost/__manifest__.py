# Copyright 2022 Patxi lersundi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Production Cost",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "version": "16.0.1.1.0",
    "depends": ["product", "mrp", "stock", "stock_move_cost"],
    "data": [
        "views/mrp_production_views.xml",
        "views/mrp_stockmove_views.xml",
        "views/mrp_workorder_views.xml",
    ],
    "installable": True,
    "post_init_hook": "_post_install_put_cost_in_productions",
}
