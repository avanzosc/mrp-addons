# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Sale Custom Values",
    "version": "18.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "purchase_stock",
        "sale_mrp",
    ],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_sale_custom_values/static/src/js/"
            "mrp_component_product_field.esm.js",
        ],
    },
    "installable": True,
    "application": False,
}
