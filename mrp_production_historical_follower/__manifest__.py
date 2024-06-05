# -*- coding: utf-8 -*-
# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Production Historical Follower",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "website": "http://www.avanzosc.com",
    "author": "AvanzOSC,",
    "license": "AGPL-3",
    
    "depends": [
        "mrp_production_historical",
        "mrp_bom_version"
    ],
    "data": [
        "data/mrp_production_historical_follower.xml",
        "views/mrp_production_views.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
}
