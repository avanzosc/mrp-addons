# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Product Configurator",
    "version": "18.0.1.0.0",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "sale",
    ],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_product_configurator/static/src/js/mrp_product_field.esm.js",
            "mrp_product_configurator/static/src/xml/mrp_product_field.xml",
        ],
    },
    "installable": True,
    "application": False,
}
