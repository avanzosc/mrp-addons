# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()

        if self.raw_material_production_id:
            action["views"] = [
                (self.env.ref("mrp.view_stock_move_operations_raw").id, "form")
            ]
            action["context"].update(
                {
                    "show_destination_location": False,
                    "force_manual_consumption": True,
                    "active_mo_id": self.raw_material_production_id.id,
                    "show_lots_m2o": True,
                    "show_lots_text": False,
                }
            )

        elif self.production_id:
            action["views"] = [
                (self.env.ref("mrp.view_stock_move_operations_finished").id, "form")
            ]
            action["context"].update(
                {
                    "show_source_location": False,
                    "show_reserved_quantity": False,
                    "show_lots_m2o": False,
                    "show_lots_text": True,
                }
            )

        return action
