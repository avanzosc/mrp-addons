# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Workorder Availability",
    'version': '14.0.1.0.0',
    "author": "Avanzosc",
    "website": "https://www.avanzosc.es",
    "category": "MRP",
    "depends": [
        "mrp",
        "stock_move_availability"
    ],
    "data": [
        "views/mrp_workorder_views.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}
