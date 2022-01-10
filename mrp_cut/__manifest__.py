# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Cut",
    'version': '14.0.1.0.0',
    "author": "Avanzosc",
    "website": "http://www.avanzosc.es",
    "category": "MRP",
    "depends": [
        "product_second_uom",
        "mrp",
        "product_dimension"
    ],
    "data": [
        "views/mrp_bom_views.xml",
        "views/mrp_production.xml"
    ],
    "license": "AGPL-3",
    'installable': True,
}
