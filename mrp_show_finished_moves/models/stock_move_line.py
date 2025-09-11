from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("move_id") and not vals.get("lot_name"):
                move = self.env["stock.move"].browse(vals["move_id"])
                if (
                    move.production_id
                    and move.product_id.tracking == "lot"
                    and not move.raw_material_production_id
                    and move.production_id.lot_producing_id
                ):
                    vals["lot_name"] = move.production_id.lot_producing_id.name
        move_lines = super().create(vals_list)
        for ml in move_lines:
            move = ml.move_id
            if move and move.production_id and not move.raw_material_production_id:
                ml.reserved_uom_qty = 0.0
        return move_lines
