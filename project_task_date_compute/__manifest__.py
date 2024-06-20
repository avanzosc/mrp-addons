
{
    'name': 'Project Task Date Compute',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Compute start and end dates for tasks based on timesheets',
    'description': 'Adds fields to compute task start and end dates based on hour entries and stage status',
    'author': 'Your Name',
    'depends': ['project', 'hr_timesheet', 'mrp_sale_info'],
    'data': [
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
}
