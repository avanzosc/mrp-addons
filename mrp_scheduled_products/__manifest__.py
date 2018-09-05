# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Scheduled Production Lines",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_view.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
