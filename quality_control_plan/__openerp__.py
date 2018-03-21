# -*- coding: utf-8 -*-
# Copyright 2018 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Quality Control Plan",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "category": "Quality control",
    "depends": [
        "quality_control",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/purchase_order_view.xml",
        "views/qc_test_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
