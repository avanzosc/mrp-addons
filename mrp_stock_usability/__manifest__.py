# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Manufacturing - Stock Usability",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "mrp",
    ],
    "excludes": [],
    "data": [
        "security/mrp_stock_usability_groups.xml",
        "views/mrp_workorder_view.xml",
        "views/res_config_settings_view.xml",
        "views/stock_move_view.xml",
    ],
    "installable": True,
}
