# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'MRP Production Erase',
    'version': '12.0.1.0.0',
    'depends': [
        'base',
        'mrp',
        'product',
    ],
    'author':  "AvanzOSC",
    'license': "AGPL-3",
    'summary': '''MRP Production Erase''',
    'website': 'http://www.avanzosc.es',
    'data': [
        'wizard/mrp_production_erase_view.xml',
    ],
    'installable': True,
}
