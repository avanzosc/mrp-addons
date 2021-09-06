# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Workorder data in worksheet header",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "mrp_workorder_grouping_by_material",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "data": [
        "views/mrp_workorder_view.xml",
        "report/mrp_workorder_line_report.xml",
        "wizard/binary_container_view.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ["PyPDF2"]
    },
}
