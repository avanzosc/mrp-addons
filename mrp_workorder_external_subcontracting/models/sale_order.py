from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
        ondelete="set null",
    )
