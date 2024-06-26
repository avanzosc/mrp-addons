# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends("purchase_line_id", "sale_line_id",
                 "raw_material_production_id", "production_id")
    def _compute_saca_line_id(self):
        super(StockMove, self)._compute_saca_line_id()
        for move in self:
            saca_line = False
            if move.purchase_line_id:
                saca_line = move.purchase_line_id.saca_line_id.id
            elif move.sale_line_id:
                saca_line = move.sale_line_id.saca_line_id.id
            elif move.production_id:
                saca_line = move.production_id.saca_line_id.id
            elif move.raw_material_production_id:
                saca_line = move.raw_material_production_id.saca_line_id.id
            move.saca_line_id = saca_line
