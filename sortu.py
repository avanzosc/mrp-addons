import os

# Definición de la estructura del módulo
MODULE_NAME = 'project_mrp'
DEPENDENCIES = ['base', 'project', 'mrp', 'sale']

MODEL_TASKS = """\
from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    mrp_production_id = fields.Many2one('mrp.production', string='Manufacturing Order', domain="[('sale_id', '=', sale_line_id.order_id.id)]")
    product_id = fields.Many2one(related='mrp_production_id.product_id', string='Product', store=True)
    verification_by = fields.Selection([
        ('unverified', 'Unverified'),
        ('sent', 'Sent'),
        ('prototype', 'By Prototype'),
        ('antiquity', 'By Antiquity'),
        ('plan', 'By Plan')
    ], string='Verification By')
    preparation = fields.Selection([
        ('closed_box', 'Closed Box'),
        ('open_box', 'Open Box'),
        ('only_bodies', 'Only Bodies'),
        ('only_lids', 'Only Lids'),
        ('only_fronts', 'Only Fronts'),
        ('no_preparation', 'No Preparation')
    ], string='Preparation')
    
    @api.depends('timesheet_ids.date')
    def _compute_start_date(self):
        for task in self:
            task.start_date = min(task.timesheet_ids.mapped('date')) if task.timesheet_ids else False

    @api.depends('timesheet_ids.date')
    def _compute_end_date(self):
        for task in self:
            task.end_date = max(task.timesheet_ids.mapped('date')) if task.timesheet_ids and task.stage_id.is_closing_stage else False

    start_date = fields.Date(compute='_compute_start_date', string='Start Date', store=True)
    end_date = fields.Date(compute='_compute_end_date', string='End Date', store=True)
"""

MODEL_MRP_PRODUCTION = """\
from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    task_ids = fields.One2many('project.task', 'mrp_production_id', string='Related Tasks')
"""

MODEL_PRODUCT_TEMPLATE = """\
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    verification_by = fields.Selection([
        ('unverified', 'Unverified'),
        ('sent', 'Sent'),
        ('prototype', 'By Prototype'),
        ('antiquity', 'By Antiquity'),
        ('plan', 'By Plan')
    ], string='Verification By')
    preparation = fields.Selection([
        ('closed_box', 'Closed Box'),
        ('open_box', 'Open Box'),
        ('only_bodies', 'Only Bodies'),
        ('only_lids', 'Only Lids'),
        ('only_fronts', 'Only Fronts'),
        ('no_preparation', 'No Preparation')
    ], string='Preparation')
"""

MODEL_PROJECT_PROJECT = """\
from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_hourly_rate = fields.Float(string='Sale Hourly Rate', default=50.0)
"""

VIEW_PROJECT_TASK_FORM = """\
<?xml version="1.0"?>
<odoo>
    <data>
        <!-- Herencia de la vista de formulario de tareas -->
        <record id="view_task_form_inherit" model="ir.ui.view">
            <field name="name">project.task.form.inherit</field>
            <field name="model">project.task</field>
            <field name="inherit_id" ref="project.view_task_form2"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='product_qty']" position="after">
                    <field name="produced_quantity"/>
                    <field name="shortage_quantity"/>
                    <field name="rejected_quantity"/>
                    <field name="operator_id"/>
                    <field name="quality_responsible_id"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
"""

VIEW_PROJECT_TASK_TREE = """\
<?xml version="1.0"?>
<odoo>
    <data>
        <!-- Herencia de la vista de árbol de tareas -->
        <record id="view_task_tree_inherit" model="ir.ui.view">
            <field name="name">project.task.tree.inherit</field>
            <field name="model">project.task</field>
            <field name="inherit_id" ref="project.view_task_tree2"/>
            <field name="arch" type="xml">
                <xpath expr="//tree" position="inside">
                    <field name="produced_quantity"/>
                    <field name="shortage_quantity"/>
                    <field name="rejected_quantity"/>
                    <field name="operator_id"/>
                    <field name="quality_responsible_id"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
"""

VIEW_MRP_PRODUCTION_FORM = """\
<?xml version="1.0"?>
<odoo>
    <data>
        <!-- Herencia de la vista de formulario de OF -->
        <record id="view_mrp_production_form_inherit" model="ir.ui.view">
            <field name="name">mrp.production.form.inherit</field>
            <field name="model">mrp.production</field>
            <field name="inherit_id" ref="mrp.mrp_production_form_view"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='product_qty']" position="after">
                    <field name="produced_quantity"/>
                    <field name="shortage_quantity"/>
                    <field name="rejected_quantity"/>
                    <field name="operator_id"/>
                    <field name="quality_responsible_id"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
"""

VIEW_MRP_PRODUCTION_TREE = """\
<?xml version="1.0"?>
<odoo>
    <data>
        <!-- Herencia de la vista de árbol de OF -->
        <record id="view_mrp_production_tree_inherit" model="ir.ui.view">
            <field name="name">mrp.production.tree.inherit</field>
            <field name="model">mrp.production</field>
            <field name="inherit_id" ref="mrp.mrp_production_tree_view"/>
            <field name="arch" type="xml">
                <xpath expr="//tree" position="inside">
                    <field name="produced_quantity"/>
                    <field name="shortage_quantity"/>
                    <field name="rejected_quantity"/>
                    <field name="operator_id"/>
                    <field name="quality_responsible_id"/>
                </xpath>
            </field>
        </record>
    </data>
</odoo>
"""

MANIFEST_CONTENT = """\
{
    'name': 'Project MRP Integration',
    'version': '1.0',
    'category': 'Project',
    'depends': %s,
    'data': [
        'views/project_task_views.xml',
        'views/mrp_production_views.xml',
        'views/product_template_views.xml',
        'views/project_project_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
""" % str(DEPENDENCIES)

# Función para crear la estructura del módulo
def create_module_structure(module_name):
    module_path = os.path.join(os.getcwd(), module_name)
    os.makedirs(module_path)

    # Crear __init__.py
    with open(os.path.join(module_path, '__init__.py'), 'w') as f:
        f.write("from . import models\n")

    # Crear carpeta models y __init__.py dentro de models
    models_path = os.path.join(module_path, 'models')
    os.makedirs(models_path)
    with open(os.path.join(models_path, '__init__.py'), 'w') as f:
        f.write("from . import project_task, mrp_production, product_template, project_project\n")

    # Crear archivo project_task.py
    with open(os.path.join(models_path, 'project_task.py'), 'w') as f:
        f.write(MODEL_TASKS)

    # Crear archivo mrp_production.py
    with open(os.path.join(models_path, 'mrp_production.py'), 'w') as f:
        f.write(MODEL_MRP_PRODUCTION)

    # Crear archivo product_template.py
    with open(os.path.join(models_path, 'product_template.py'), 'w') as f:
        f.write(MODEL_PRODUCT_TEMPLATE)

    # Crear archivo project_project.py
    with open(os.path.join(models_path, 'project_project.py'), 'w') as f:
        f.write(MODEL_PROJECT_PROJECT)

    # Crear carpeta views
    views_path = os.path.join(module_path, 'views')
    os.makedirs(views_path)

    # Crear archivos de vista
    with open(os.path.join(views_path, 'project_task_views.xml'), 'w') as f:
        f.write(VIEW_PROJECT_TASK_FORM)
    with open(os.path.join(views_path, 'mrp_production_views.xml'), 'w') as f:
        f.write(VIEW_MRP_PRODUCTION_FORM)
    with open(os.path.join(views_path, 'product_template_views.xml'), 'w') as f:
        f.write(VIEW_PROJECT_TASK_TREE)
    with open(os.path.join(views_path, 'project_project_views.xml'), 'w') as f:
        f.write(VIEW_MRP_PRODUCTION_TREE)

    # Crear archivo de manifiesto
    with open(os.path.join(module_path, '__manifest__.py'), 'w') as f:
        f.write(MANIFEST_CONTENT)

# Crear el módulo
create_module_structure(MODULE_NAME)
