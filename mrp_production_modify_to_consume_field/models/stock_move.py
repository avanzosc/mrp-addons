# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    readonly_to_consume = fields.Boolean(compute="_compute_readonly_to_consume")

    def _compute_readonly_to_consume(self):
        for move in self:
            if self.env.user.has_group(
                "mrp_production_modify_to_consume_field.group_allow_modify_to_consume_field"
            ):
                move.readonly_to_consume = False
            else:
                move.readonly_to_consume = True
