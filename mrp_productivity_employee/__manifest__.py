# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Productivity Employee",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": ["mrp", "mrp_usability", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_department_views.xml",
        "views/mrp_workcenter_views.xml",
        "views/mrp_workorder_views.xml",
        "wizard/wiz_update_workorder_productivity_views.xml",
    ],
    "installable": True,
}
