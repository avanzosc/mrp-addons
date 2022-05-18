# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP BoM Import",
    "version": "14.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "depends": [
        "base",
        "mrp",
        "product",
    ],
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "website": "https://github.com/avanzosc/mrp-addons",
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_bom_view.xml",
        "views/product_view.xml",
    ],
    "installable": True,
}
