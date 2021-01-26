# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Product version",
    "version": "12.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "product",
    ],
    "excludes": [
        "product_variant_configurator",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Tools",
    "data": [
        "security/ir.model.access.csv",
        "views/product_version_view.xml",
        "views/product_attribute_view.xml",
        "views/product_product_view.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
