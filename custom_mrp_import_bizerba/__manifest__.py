# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Custom MRP Import Bizerba",
    "version": "14.0.1.0.0",
    "category": "MRP",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "mrp",
        "base_import_wizard",
        "custom_mrp_descarga"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/product_qty_decimal_precision.xml",
        "views/product_template_view.xml",
        "views/mrp_production_view.xml",
        "views/bizerba_import_line_view.xml",
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "installable": True,
}
