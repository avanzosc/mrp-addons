# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_loss_qty = fields.Float(
        string="Loss quantity",
        related="product_id.product_loss_qty",
        digits="Product Unit of Measure",
    )
