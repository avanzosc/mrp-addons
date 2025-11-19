# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Production Control",
    "summary": "Production control tracking for Work Orders and Manufacturing Orders.",
    "version": "16.0.1.1.0",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing",
    "data": [
        "views/mrp_production_control_views.xml",
        "views/mrp_workorder_view.xml",
        "views/mrp_production_view.xml",
        "views/product_template_view.xml",
        "views/qc_inspection_type_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
}
