# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Workorder Finish Button",
    'version': '14.0.1.0.0',
    "author": "Avanzosc",
    "website": "https://www.avanzosc.es",
    "category": "MRP",
    "depends": [
        "mrp_workorder_availability",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mrp_workorder_finish_wizard_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}
