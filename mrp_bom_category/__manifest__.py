# Copyright 2022 Gonzalo Nuin - AvanzOSC
# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BOM categories",
    "version": "14.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_bom_views.xml",
        "views/mrp_bom_category_views.xml",
    ],
    "installable": True,
}
