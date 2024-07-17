{
    'name': 'MRP BOM Extension',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Add a computed column to the MRP BOM lines',
    'description': '''
        This module adds a new column to the MRP BOM lines that shows the product quantity multiplied by the product price.
    ''',
    'depends': ['mrp'],
    'data': [
        'views/mrp_bom_line_templates.xml',
    ],
    'installable': True,
    'application': False,
}
