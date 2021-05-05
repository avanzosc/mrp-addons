# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Product version dimensions in purchase order",
    "version": "12.0.1.0.2",
    "license": "AGPL-3",
    "depends": [
        "purchase_discount",
        "product_variant_custom_purchase",
        "product_variant_custom_dimensions",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "",
    "data": [
        "views/purchase_order_view.xml",
        "views/account_invoice_line_view.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
