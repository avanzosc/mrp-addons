{
    "name": "MRP Manufacturing Order Stock Picking Link",
    "version": "16.0.1.0.0",
    "summary": "Link between manufacturing orders and internal stock pickings.",
    "category": "Manufacturing",
    "author": "Avanzosc",
    "website": "https://github.com/avanzosc/mrp-addons",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "stock",
    ],
    "data": [
        "views/mrp_production_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
