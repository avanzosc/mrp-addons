from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()
        action["target"] = "current"
        action["context"] = action.get("context", {})

        return action
