{
    'name': 'Project MRP Integration',
    'version': '1.0',
    'category': 'Project',
    'depends': ['base', 'project', 'mrp', 'sale'],
    'data': [
        'views/project_task_views.xml',
        'views/mrp_production_views.xml',
        'views/product_template_views.xml',
        'views/project_project_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
