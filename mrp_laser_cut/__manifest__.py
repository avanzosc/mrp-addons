# Copyright 2026 Inael
# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Laser Cut",
    "summary": "Cut several finished products from one unit of raw material "
    "on a laser work center",
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
        "data/mrp_laser_cut_order_sequence.xml",
        "views/mrp_workcenter_views.xml",
        "views/mrp_bom_views.xml",
        "views/product_template_views.xml",
        "views/mrp_laser_cut_order_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_warehouse_orderpoint_views.xml",
    ],
    "demo": [
        "demo/mrp_laser_cut_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_laser_cut/static/src/scss/mrp_laser_cut.scss",
        ],
    },
    "installable": True,
}
