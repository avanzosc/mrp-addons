# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Mrp BoM Line Product Brand Info",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "author": "Avanzosc",
    "license": "AGPL-3",
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
        "mrp_bom_report",
        "product_brand_supplierinfo",
    ],
    "data": [
        "report/mrp_bom_report.xml",
        "views/mrp_bom_line_views.xml",
        "views/mrp_bom_views.xml",
    ],
    "installable": True,
}
