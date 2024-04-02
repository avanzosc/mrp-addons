# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Stock Picking Create Repair",
    "version": "14.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "Avanzosc",
    "website": "https://www.avanzosc.es",
    "depends": [
        "stock_picking_create_repair",
        "mrp",
    ],
    "data": [
        "views/mrp_workcenter_views.xml",
        "views/repair_order_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
