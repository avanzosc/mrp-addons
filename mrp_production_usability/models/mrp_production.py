from odoo import models, fields

from odoo import models, fields

class MrpProductionUsability(models.Model):
    _inherit = 'mrp.production'
    _description = 'Production Usability'

    produced_quantity = fields.Float(string='Produced Quantity')
    shortage_quantity = fields.Float(string='Shortage Quantity')
    rejected_quantity = fields.Float(string='Rejected Quantity')
    operator_id = fields.Many2one('hr.employee', string='Operator')
    quality_responsible_id = fields.Many2one('hr.employee', string='Quality Responsible')
