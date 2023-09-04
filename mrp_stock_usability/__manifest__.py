# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Manufacturing - Stock Usability",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
        # "base_view_inheritance_extension",
    ],
    "data": [
        "security/mrp_stock_usability_groups.xml",
        "views/mrp_production_views.xml",
        "views/mrp_workorder_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
}
