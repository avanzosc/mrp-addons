# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP BoM Cost Full",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Avanzosc",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing/Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/mrp_bom_views.xml",
        "views/mrp_routing_workcenter_views.xml",
    ],
    "installable": True,
    "post_init_hook": "_post_install_mrp_bom_cost_full",
}
