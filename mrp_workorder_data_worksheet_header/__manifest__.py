# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Workorder data in worksheet header",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "mrp_workorder_grouping_by_material",
        "pdf_previewer",
    ],
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing",
    "data": [
        "views/mrp_workorder_view.xml",
        "views/mrp_workorder_nest_view.xml",
        "views/mrp_workorder_nest_line_view.xml",
        "report/mrp_workorder_report.xml",
        "report/mrp_workorder_nest_line_report.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["PyPDF2"]},
}
