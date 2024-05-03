# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Stock Move Cost",
    "version": "16.0.1.1.0",
    "category": "Manufacturing/Manufacturing",
    "website": "https://avanzosc.es/",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "depends": [
        "stock_move_cost",
        "mrp",
    ],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "installable": True,
    "post_init_hook": "_post_install_put_cost_in_productions",
}
