# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp QR Label",
    "version": "16.0.1.0.0",
    "author": "Avanzosc",
    "website": "https://github.com/avanzosc/mrp-addons",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "depends": ["mrp", "stock_product_qr_label"],
    "data": [
        "report/mrp_finished_product_qr_label.xml",
        "report/mrp_product_to_consume_qr_label.xml",
        "report/mrp_consumed_product_qr_label.xml",
    ],
    "installable": True,
}
