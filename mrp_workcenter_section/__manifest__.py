# Copyright 2026 Berezi Amubieta
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sections in MRP Workcenters",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "version": "18.0.1.0.0",
    "depends": [
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workcenter_view.xml",
        "views/mrp_workorder_view.xml",
    ],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
}
