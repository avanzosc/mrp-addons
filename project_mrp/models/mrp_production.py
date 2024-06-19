from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    task_ids = fields.One2many('project.task', 'mrp_production_id', string='Related Tasks')
