# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Production Quality Operator Custom Fields",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Fields qty_rejected, operator_id and quality_responsible_id to production",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "license": "AGPL-3",
    "depends": ["mrp", "hr"],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
