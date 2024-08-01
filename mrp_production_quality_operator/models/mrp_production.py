from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    qty_rejected = fields.Float(string="Rejected Quantity")
    operator_id = fields.Many2one(comodel_name="hr.employee", string="Operator")
    quality_responsible_id = fields.Many2one(
        comodel_name="hr.employee", string="Quality Responsible"
    )
