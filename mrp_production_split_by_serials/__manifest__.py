# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Production Split By Serials",
    "version": "14.0.1.1.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
        "stock"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wiz_split_serials_views.xml",
    ],
    "installable": True,
}
