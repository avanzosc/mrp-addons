# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    qr_code = fields.Char(string="QR Code", compute="_compute_qr_code")

    def _compute_qr_code(self):
        for move in self:
            move.qr_code = (
                move.product_id.code if move.product_id.code else move.product_id.name
            )
