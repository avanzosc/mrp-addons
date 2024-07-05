# (c) Ana Iris Castro Ramírez - Guadaltech
# (c) Ignacio Ales López - Guadaltech
# (c) 2024 Alfredo de la Fuente - Avanzosc
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    production_lot_info = fields.Text(compute="_compute_production_lot_info")

    @api.depends(
        "move_line_ids",
        "move_line_ids.lot_id",
        "move_line_ids.lot_id.name",
        "move_line_ids.qty_done",
    )
    def _compute_production_lot_info(self):
        for move in self:
            move.production_lot_info = ""
            if move.raw_material_production_id and move.product_id.tracking != "none":
                production_info = []
                for move_line in move.move_line_ids:
                    production_info.append(
                        f"{move_line.lot_id.name or 'N/A'} ("
                        "{move_line.reserved_uom_qty or move_line.qty_done})"
                    )
                move.production_lot_info = ", ".join(production_info)
