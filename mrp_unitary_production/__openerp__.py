# -*- coding: utf-8 -*-
# Copyright 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP unitary production",
    "version": "8.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "mrp",
    ],
    "data": [
        "wizard/mrp_product_produce_view.xml",
        "views/mrp_bom_view.xml",
        "views/mrp_production_view.xml",
        "views/mrp_routing_view.xml",
    ],
    "installable": True,
}
