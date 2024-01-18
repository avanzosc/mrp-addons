# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MRP BoM Import',
    'version': '12.0.1.0.0',
    'depends': [
        'base',
        'mrp',
        'product',
    ],
    'author':  "AvanzOSC",
    'license': "AGPL-3",
    'summary': '''MRP BoM Import''',
    'website': 'http://www.avanzosc.es',
    'data': [
        'views/mrp_bom_view.xml',
        'views/product_view.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
    'auto_install': False,
}
