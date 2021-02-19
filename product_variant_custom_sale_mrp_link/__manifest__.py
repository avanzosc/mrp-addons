# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Glue module sale_line_mrp_link version modules",
    "version": "12.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "sale_line_mrp_link",
        "product_variant_custom_sale",
        "mrp_production_custom_variants_inherited_attributes",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "",
    "data": [
        "views/sale_order_line_view.xml",
        "views/mrp_production_view.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
}
