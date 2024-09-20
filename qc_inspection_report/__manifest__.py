# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Qc Inspection Report",
    "version": "16.0.1.0.0",
    "category": "Quality Control",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": ["partner_fax", "quality_control_oca", "quality_control_stock_oca"],
    "data": [
        "views/res_company_views.xml",
        "reports/external_layout_qc_inspection.xml",
        "reports/qc_inspection_report.xml",
    ],
    "installable": True,
}
