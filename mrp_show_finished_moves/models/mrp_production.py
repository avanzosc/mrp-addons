# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_show_finished_move_lines(self):
        self.ensure_one()
        related_productions = self.env["mrp.production"].search(
            [("procurement_group_id", "=", self.procurement_group_id.id)]
        )
        finished_lines = related_productions.mapped("move_finished_ids.move_line_ids")
        return {
            "type": "ir.actions.act_window",
            "name": "Finished Move Lines",
            "view_mode": "tree",
            "res_model": "stock.move.line",
            "domain": [("id", "in", finished_lines.ids)],
            "context": {"default_procurement_group_id": self.procurement_group_id.id},
        }

    @api.depends(
        "workorder_ids.state", "move_finished_ids", "move_finished_ids.quantity_done"
    )
    def _get_produced_qty(self):
        for production in self:
            done_moves = production.move_finished_ids.filtered(
                lambda x: x.state != "cancel"
                and x.product_id.id == production.product_id.id
                and production.state == "done"
            )
            qty_produced = sum(done_moves.mapped("quantity_done"))
            production.qty_produced = qty_produced
        return True
