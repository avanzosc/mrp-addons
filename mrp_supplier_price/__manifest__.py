# Copyright 2016 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Supplier Price in Scheduled Manufacturing Products",
    "version": "11.0.2.0.0",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "mrp_scheduled_products",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "data": [
        "security/mrp_supplier_price_groups.xml",
        "views/mrp_production_view.xml",
        "views/res_config_view.xml",
    ],
    "installable": True,
}
