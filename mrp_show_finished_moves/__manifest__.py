# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Show Finished Moves",
    "summary": "Improves the visibility of finished moves within MOs and WOs",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_view.xml",
        "views/mrp_workorder_view.xml",
        "views/stock_move_views.xml",
        "views/stock_move_line_views.xml",
        "wizard/mrp_production_qty_warning.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_show_finished_moves/static/src/**/*.js",
        ],
    },
    "installable": True,
    "application": False,
}
