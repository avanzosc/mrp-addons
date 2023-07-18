# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Workorders grouping by main material",
    "version": "13.0.3.0.0",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "mrp_stock_usability",
        "product_expiry",
        "pdf_previewer",
    ],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing",
    "data": [
        "data/mrp_workorder_nest_data.xml",
        "security/ir.model.access.csv",
        "security/mrp_workorder_grouping_by_material_security.xml",
        "views/mrp_bom_view.xml",
        "views/mrp_production_view.xml",
        "views/mrp_workcenter_view.xml",
        "views/mrp_workorder_nest_view.xml",
        "views/mrp_workorder_nest_line_view.xml",
        "views/mrp_workorder_view.xml",
        "wizard/nested_new_line_view.xml",
        "wizard/multiple_copy_view.xml",
    ],
    "external_dependencies": {"python": ["PyPDF2"]},
    "installable": True,
}
