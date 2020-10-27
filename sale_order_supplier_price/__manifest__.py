# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale order supplier price",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "mrp_supplier_price",
        "sale_line_mrp_link",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "",
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_view.xml",
        "views/mrp_production_product_line_view.xml",
        "views/product_category_view.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
