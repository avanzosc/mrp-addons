# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Production inherited attributes",
    "version": "12.0.2.0.0",
    "license": "AGPL-3",
    "depends": [
        "mrp_hook",
        "mrp_scheduled_products",
        "mrp_bom_component_menu",
        "product_variant_custom",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_view.xml",
        "views/mrp_bom.xml",
        "views/product_attribute_view.xml",
        "views/mrp_workorder_view.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
