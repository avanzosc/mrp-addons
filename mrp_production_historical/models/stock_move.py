# Copyright 2014 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        if "from_scrap" not in self.env.context:
            for move in moves.filtered(
                lambda x: x.raw_material_production_id and not x.bom_line_id
            ):
                move.create_mrp_production_historical()
        return moves

    def create_mrp_production_historical(self):
        vals = self._get_vals_to_create_mrp_production_historical()
        self.env["mrp.production.historical"].with_context(add_historical=True).create(
            vals
        )

    def _get_vals_to_create_mrp_production_historical(self):
        vals = {
            "production_id": self.raw_material_production_id.id,
            "historical_date": fields.Datetime.now(),
            "type": "add",
            "user_id": self.env.user.id,
            "product_id": self.product_id.id,
            "programed_qty": self.product_uom_qty,
        }
        return vals
