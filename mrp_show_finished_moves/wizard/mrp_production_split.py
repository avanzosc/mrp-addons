# Copyright 2026 AvanzOSC - Lucía Echeverría
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpProductionSplit(models.TransientModel):
    _inherit = "mrp.production.split"

    def action_split(self):
        production = self.production_id
        if production._is_splittable_multiple_serial_production():
            raw_moves = production.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            ).with_context(skip_auto_pick=True, skip_qty_producing_sync=True)
            raw_moves.move_line_ids.picked = False
            raw_moves.picked = False
        return super().action_split()
