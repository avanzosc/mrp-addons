# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Production Prototype",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "installable": True,
    "post_init_hook": "_post_install_put_non_prototype_in_mrp_production",
}
