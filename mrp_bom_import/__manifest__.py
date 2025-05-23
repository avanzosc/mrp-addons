# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP BoM Import",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "base",
        "mrp",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_bom_import_view.xml",
        "views/mrp_bom_import_line_view.xml",
        "views/mrp_bom_line_view.xml",
        "views/product_view.xml",
    ],
    "installable": True,
}
