# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.tools import float_compare, float_is_zero

ACTIVE_STATES = {"confirmed", "progress", "to_close"}


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _is_syncable_finished_move(self, move):
        production = move.production_id
        return bool(
            production
            and move.product_id == production.product_id
            and not move.scrapped
            and production.state in ACTIVE_STATES
        )

    def _is_raw_consumption_move(self):
        self.ensure_one()
        production = self.raw_material_production_id
        return bool(
            production
            and self.state not in ("done", "cancel")
            and production.state in ACTIVE_STATES
        )

    def _auto_pick_if_consumed(self):
        rounding = self.product_uom.rounding
        should = self.should_consume_qty

        if float_is_zero(should, precision_rounding=rounding):
            return

        if (
            float_compare(self.quantity, should, precision_rounding=rounding) >= 0
            and not self.picked
        ):
            self.with_context(skip_qty_producing_sync=True).picked = True

    def _check_raw_moves_picked(self):
        if self.env.context.get("skip_auto_pick"):
            return
        for move in self.with_context(skip_auto_pick=True):
            if move._is_raw_consumption_move():
                move._auto_pick_if_consumed()

    def _compute_quantity(self):
        ctx = self.env.context
        qty_before = {}
        if not ctx.get("skip_qty_producing_sync"):
            qty_before = {
                move.id: move.production_id.qty_producing
                for move in self
                if self._is_syncable_finished_move(move)
            }

        res = super()._compute_quantity()

        for move in self.filtered(lambda m: m.id in qty_before):
            if float_compare(
                move.quantity,
                qty_before[move.id],
                precision_rounding=move.product_uom.rounding,
            ):
                move.production_id.with_context(
                    skip_qty_producing_sync=True,
                    skip_serial_regeneration=True,
                )._sync_qty_producing_from_move(move.quantity)

        self._check_raw_moves_picked()
        return res

    def _set_quantity(self):
        syncable = self.filtered(self._is_syncable_finished_move)
        res = super()._set_quantity()

        if not self.env.context.get("skip_qty_producing_sync"):
            for move in syncable:
                move.production_id.with_context(
                    skip_qty_producing_sync=True,
                    skip_serial_regeneration=True,
                )._sync_qty_producing_from_move(move.quantity)

        self._check_raw_moves_picked()
        return res

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()
        action["target"] = "current"
        ctx = action.setdefault("context", {})

        production = self.production_id
        product = self.product_id

        if production and product.tracking != "none" and self.state != "done":
            ctx["show_lot_name_instead_lot_id"] = True

        if (
            production
            and product.tracking == "serial"
            and production.product_id == product
            and self.state != "done"
        ):
            ctx.update(
                {
                    "mo_next_serial": production._increment_serial_number(
                        production.last_manufactured_lot
                    )
                    or "",
                    "mo_product_qty": int(production.product_qty),
                }
            )

        return action

    def _compute_forecast_information(self):
        res = super()._compute_forecast_information()
        for move in self.filtered(
            lambda m: m.raw_material_production_id
            and m.state in ("assigned", "partially_available")
            and float_compare(
                m.quantity,
                m.should_consume_qty,
                precision_rounding=m.product_uom.rounding,
            )
            >= 0
        ):
            move.forecast_availability = move.product_qty
        return res

    @api.depends(
        "has_tracking",
        "picking_type_id.use_create_lots",
        "picking_type_id.use_existing_lots",
        "state",
    )
    def _compute_display_assign_serial(self):
        res = super()._compute_display_assign_serial()
        for move in self.filtered(
            lambda m: m.product_id.tracking == "serial"
            and m.production_id
            and m.production_id.product_id == m.product_id
        ):
            move.display_assign_serial = True
        return res
