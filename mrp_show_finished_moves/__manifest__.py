# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Show Finished Moves",
    "summary": "Improves the visibility of finished moves within MOs and WOs",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing",
    "data": [
        "views/mrp_production_view.xml",
        "views/mrp_workorder_view.xml",
        "views/stock_move_views.xml",
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
    "application": False,
}
