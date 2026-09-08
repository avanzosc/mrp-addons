# Copyright 2026 Inael
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Laser Cut",
    "summary": "Laser cutting orders: one raw sheet, several finished products",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Inael, AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/order_olaser_sequence.xml",
        "views/mrp_workcenter_views.xml",
        "views/mrp_bom_views.xml",
        "views/product_template_views.xml",
        "views/order_olaser_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_warehouse_orderpoint_views.xml",
    ],
    "installable": True,
}
