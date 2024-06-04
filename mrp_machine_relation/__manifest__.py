# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# Copyright 2015 Daniel Campos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Machine Relation",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "description": """
    This modules links mrp.workcenters and machines.
    """,
    "author": "OdooMRP team," "Avanzosc," "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": ["Daniel Campos <danielcampos@avanzosc.es>"],
    "website": "https://github.com/avanzosc/mrp-addons",
    "depends": [
        "mrp",
        "machine_manager",
    ],
    "data": ["views/mrp_workcenter_view.xml"],
    "installable": True,
    "auto_install": True,
}
