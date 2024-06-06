# -*- coding: utf-8 -*-
# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# Copyright 2014 Daniel Campos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP BoM Version Component Change",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "license": "AGPL-3",
    "website": "http://avanzosc.com",
    "depends": [
        "mrp_bom_component_change",
        "mrp_bom_version"
    ],
    "data": [
        "views/mrp_bom_change_view.xml",
             ],
    "installable": True,
    "auto_install": True,
}
