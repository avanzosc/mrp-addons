# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Subcontracting Owner",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "author": "Avanzosc",
    "license": "AGPL-3",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp_subcontracting",
        "mrp_production_owner",
    ],
    "data": [
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
