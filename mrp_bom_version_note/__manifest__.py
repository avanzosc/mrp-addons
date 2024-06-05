# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Bom Version Note",
    "version": "16.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "website": "http://www.avanzosc.com",
    "author": "AvanzOSC,",
    "license": "AGPL-3",
    "summary": "BoM notes",
    
    "depends": [
        "mrp_bom_version",
        "mrp_bom_note",
    ],
    "data": [
        "views/mrp_bom_views.xml"
    ],
    "installable": True,
    "auto_install": True,
}
