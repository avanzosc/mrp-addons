# Copyright 2026 Inael
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class OrderOlaserRechazo(models.Model):
    _name = "order.olaser.rechazo"
    _description = "Laser Cutting Order Rejects"

    olaser_id = fields.Many2one(
        comodel_name="order.olaser", string="Laser Order", ondelete="cascade"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        domain=[("is_laser_cut", "=", True)],
    )
    cantidad = fields.Float(string="Rejected Quantity", required=True)
    procesado = fields.Boolean(string="Processed", default=False)
