# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Product Version To BOM",
    'version': '14.0.1.0.0',
    "author": "Avanzosc",
    "website": "http://www.avanzosc.es",
    "category": "MRP",
    "depends": [
        "product",
        "mrp"
    ],
    "data": [
        "views/mrp_bom_views.xml",
        "views/product_template_views.xml",
        "views/mrp_production_views.xml"
    ],
    "license": "AGPL-3",
    'installable': True,
}
