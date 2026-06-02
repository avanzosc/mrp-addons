# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Production Parent",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/avanzosc/mrp-addons",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "depends": ["mrp", "mrp_sale_info"],
    "data": [
        "views/mrp_production_views.xml",
        "views/sale_order_views.xml",
        "report/report_mrporder.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
