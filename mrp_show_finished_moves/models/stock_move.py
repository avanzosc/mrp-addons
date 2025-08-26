from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()
        action["target"] = "current"
        action["context"] = action.get("context", {})

        return action

    @api.onchange("quantity_done")
    def _on_change_quantity_done(self):
        for move in self:
            if move.production_id.qty_producing == 0.0:
                move.production_id.qty_producing = move.quantity_done
