from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    mrp_production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        ondelete="set null",
    )
