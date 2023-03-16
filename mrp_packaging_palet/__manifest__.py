# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Packaging Palet",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "https://github.com/avanzosc/odoo-addons",
    "website": "http://www.avanzosc.es",
    "depends": [
        "product_packaging_palet",
        "mrp_qty_by_packaging",
    ],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "installable": True,
}
