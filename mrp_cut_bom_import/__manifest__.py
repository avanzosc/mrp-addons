# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BoM import with MRP Cut",
    "version": "14.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp_bom_import",
        "mrp_cut",
    ],
    "excludes": [],
    "data": [
        "views/mrp_bom_import_view.xml",
    ],
    "installable": True,
    "autoinstall": True,
}
