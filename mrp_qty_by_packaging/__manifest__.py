# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Qty By Packaging",
    "summary": "In MOs add product packaging id and qty and packaging_id fields.",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "https://github.com/avanzosc/sale-addons",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": ["product", "sale", "mrp"],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "installable": True,
}
