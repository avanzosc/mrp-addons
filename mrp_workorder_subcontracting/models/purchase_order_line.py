from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    workorder_id = fields.Many2one(
        "mrp.workorder",
        string="Work Order",
    )
