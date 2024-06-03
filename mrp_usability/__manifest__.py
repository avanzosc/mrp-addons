# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Usability",
    "version": "12.0.2.0.0",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "category": "Hidden",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
    ],
    "data": [
        "security/mrp_usability_security.xml",
        "views/stock_move_views.xml",
        "views/mrp_production_views.xml",
        "views/mrp_workorder_views.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
