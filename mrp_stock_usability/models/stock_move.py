# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    mrp_unreserve_visible = fields.Boolean(
        string="Allowed to Unreserve Inventory",
        compute="_compute_unreserve_visible",
        help="Technical field to check when we can unreserve",
    )

    @api.depends(
        "raw_material_production_id",
        "raw_material_production_id.state",
        "picked",
        "move_line_ids",
    )
    def _compute_unreserve_visible(self):
        for move in self:
            raw_production = move.raw_material_production_id
            already_reserved = (
                bool(raw_production)
                and raw_production.state not in ("done", "cancel")
                and bool(move.move_line_ids)
            )
            move.mrp_unreserve_visible = already_reserved and not move.picked

    def button_assign(self):
        self.ensure_one()
        self._action_assign()
        return True

    def button_unreserve(self):
        self.ensure_one()
        self._do_unreserve()
        return True
