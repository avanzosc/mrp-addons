# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Production Historical",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/avanzosc/mrp-addons",
    "author": "AvanzOSC,",
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_views.xml",
        "views/mrp_bom_views.xml",
    ],
    "installable": True,
}
