# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# Copyright 2026 Eñaut Alberdi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Production Show Button Unreserve",
    "version": "14.0.1.1.0",
    "category": "MRP",
    "summary": """
    Show Manufacturing Order action buttons in the mrp.production list view
    """,
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_production_tree_buttons_view.xml",
    ],
    "installable": True,
}
