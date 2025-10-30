# Copyright 2025 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Workorder Subcontracting",
    "version": "16.0.1.0.0",
    "author": "Avanzosc",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "depends": ["mrp", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_routing_workcenter_view.xml",
        "views/product_template_views.xml",
        "views/mrp_workorder_views.xml",
        "views/purchase_order_views.xml",
        "views/mrp_workcenter_views.xml",
        "views/product_subcontracting_charge_views.xml",
    ],
    "installable": True,
    "application": False,
}
