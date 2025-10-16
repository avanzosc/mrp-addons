from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    subcon_purchase = fields.Boolean(string="suncontracting purchase", default=False)

    workorder_id = fields.Many2one("mrp.workorder", string="Work Order")

    production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        related="workorder_id.production_id",
        store=True,
        readonly=True,
    )
