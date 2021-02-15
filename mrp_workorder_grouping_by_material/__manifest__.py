# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Workorders grouping by main material",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mrp", "product_expiry"
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "data": [
        "data/mrp_workorder_nest_data.xml",
        "security/ir.model.access.csv",
        "views/mrp_bom_view.xml",
        "views/mrp_workcenter_view.xml",
        "views/mrp_workorder_nest_view.xml",
        "views/mrp_workorder_view.xml",
        "wizard/nested_new_line_view.xml",
        "wizard/nested_new_line_action_menu.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
