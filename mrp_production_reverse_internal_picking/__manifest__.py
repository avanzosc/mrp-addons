# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Production Reverse Internal Picking",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/avanzosc/mrp-addons",
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "depends": ["mrp", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wiz_reverse_internal_picking_from_of_views.xml",
    ],
    "installable": True,
}
