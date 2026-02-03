# Copyright 2026 Eñaut Alberdi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Workcenter Productivity OT Report",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "summary": ("Tracking productivity in workcenters within manufacturing"),
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
        "hr",
    ],
    "data": [
        "views/mrp_workcenter_productivity_views.xml",
    ],
    "installable": True,
    "application": False,
}
