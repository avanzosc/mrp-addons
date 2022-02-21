# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Repair Order Type",
    "version": "12.0.1.0.0",
    "category": "Manufacturing",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "license": "AGPL-3",
    "depends": [
        'repair',
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/default_type.xml",
        "views/repair_order_view.xml",
        "views/repair_order_type_view.xml",
    ],
    'installable': True,
}
