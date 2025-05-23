# Copyright 2024 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BoM Routing Workcenter Import",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "base_import_wizard",
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_routing_workcenter_import_line_view.xml",
        "views/mrp_routing_workcenter_import_view.xml",
    ],
    "installable": True,
}
