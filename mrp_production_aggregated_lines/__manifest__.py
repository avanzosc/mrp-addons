# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Manufacturing order aggregated lines",
    "version": "12.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "sale_stock",
        "mrp",
        "mrp_scheduled_products",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Tools",
    "data": [
        "views/mrp_production_view.xml",
        "views/sale_view.xml"
    ],
    'demo': [],
    'pre_init_hook': "pre_init_hook",
    'installable': True,
    'auto_install': False,
}
