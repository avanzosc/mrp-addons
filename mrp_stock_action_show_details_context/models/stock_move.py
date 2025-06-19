# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()

        if self.raw_material_production_id or self.production_id:

            picking_type = self.picking_type_id

            if picking_type.use_auto_consume_components_lots:
                action["context"]["show_lots_m2o"] = True
                action["context"]["show_lots_text"] = False
            elif picking_type.use_create_components_lots:
                action["context"]["show_lots_m2o"] = False
                action["context"]["show_lots_text"] = True
            else:
                action["context"]["show_lots_m2o"] = False
                action["context"]["show_lots_text"] = False

        return action
