# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Work Order Consume",
    "version": "16.0.1.0.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "summary": "Adds a inventory posting button and finished moves tab to work orders.",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_workorder_views.xml",
        "views/mrp_production_view.xml",
        "views/stock_move_view.xml",
    ],
    "installable": True,
}
