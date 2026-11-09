# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re

from odoo import _, api, fields, models
from odoo.tools import float_compare, float_round

ACTIVE_STATES = {"confirmed", "progress", "to_close"}


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    last_manufactured_lot = fields.Char(
        compute="_compute_last_manufactured_lot",
    )

    @api.depends("product_id")
    def _compute_last_manufactured_lot(self):
        MoveLine = self.env["stock.move.line"]
        for production in self:
            last_line = MoveLine.search(
                [
                    ("product_id", "=", production.product_id.id),
                    ("lot_id", "!=", False),
                    ("state", "=", "done"),
                ],
                order="id desc",
                limit=1,
            )
            production.last_manufactured_lot = (
                last_line.lot_id.name if last_line else False
            )

    def write(self, vals):
        old_lot_names = {}
        lot_only_change = "lot_producing_id" in vals and "qty_producing" not in vals
        if lot_only_change:
            for production in self:
                if production.product_id.tracking == "lot":
                    old_lot_names[production.id] = (
                        production.lot_producing_id.name
                        if production.lot_producing_id
                        else False
                    )

        res = super().write(vals)

        if "qty_producing" not in vals and "lot_producing_id" not in vals:
            return res

        ctx = self.env.context

        if not ctx.get("skip_action_assign"):
            self.with_context(skip_action_assign=True).action_assign()

        if ctx.get("skip_qty_producing_sync"):
            return res

        active = self.filtered(lambda p: p.state in ACTIVE_STATES)

        for production in active.filtered(lambda p: p.product_id.tracking == "serial"):
            production.with_context(
                skip_qty_producing_sync=True
            )._auto_generate_finished_serials()

        for production in active.filtered(lambda p: p.product_id.tracking == "lot"):
            if lot_only_change:
                new_name = (
                    production.lot_producing_id.name
                    if production.lot_producing_id
                    else False
                )
                old_name = old_lot_names.get(production.id)
                for move in production.move_finished_ids:
                    if (
                        move.product_id == production.product_id
                        and not move.raw_material_production_id
                    ):
                        eligible = move.move_line_ids.filtered(
                            lambda ml: ml.state not in ("done", "cancel")
                        )
                        auto = eligible.filtered(
                            lambda ml, oldn=old_name: not ml.lot_name
                            or ml.lot_name == oldn
                        )
                        if auto:
                            auto.write({"lot_name": new_name or False, "lot_id": False})
            else:
                production.with_context(
                    skip_qty_producing_sync=True
                )._auto_regenerate_lot_finished_line()

        return res

    def action_confirm(self):
        res = super().action_confirm()
        for production in self.filtered(lambda p: p.product_id.tracking == "serial"):
            production.with_context(skip_qty_producing_sync=True).write(
                {"qty_producing": production.product_qty}
            )
            production._auto_generate_finished_serials()
        return res

    @api.onchange("qty_producing", "lot_producing_id")
    def _onchange_producing(self):
        if self.product_id.tracking == "serial":
            self.sudo()._set_qty_producing(False)
            return
        return super()._onchange_producing()

    @api.onchange("lot_producing_id")
    def _onchange_lot_producing_id_warning(self):
        if (
            self._origin.id
            and self.lot_producing_id
            and self._origin.lot_producing_id != self.lot_producing_id
        ):
            return {
                "warning": {
                    "title": _("Production Lot Change"),
                    "message": _(
                        "This change will reassign the lot on all finished "
                        "product move lines that do not already have a "
                        "manually set different lot and are not in done or "
                        "cancelled state.\n\n"
                        "Save the manufacturing order to confirm, or discard"
                        " to cancel."
                    ),
                }
            }

    def button_mark_done(self):
        for production in self:
            finished_move = production.move_finished_ids.filtered(
                lambda m, p=production: m.product_id == p.product_id
            )
            if not finished_move:
                continue

            quantity_done = finished_move.quantity

            if quantity_done and quantity_done != production.qty_producing:
                return self._launch_qty_warning(
                    production,
                    _(
                        "Producing vs Done quantity mismatch detected:\n\n"
                        "• Manufacturing Order reports %(planned)s units"
                        " producing.\n"
                        "• Manufacturing Order finished moves report"
                        " %(actual)s units produced.\n\n"
                        "If you choose 'Yes', the system will:\n"
                        "1. Set 'Quantity Producing' to match 'Quantity"
                        " Done'.\n"
                        "2. Update all related WOs' 'Quantity Producing'"
                        " and 'Quantity Produced'.\n"
                        "3. Continue marking the Manufacturing Order as"
                        " done."
                    )
                    % {"planned": production.qty_producing, "actual": quantity_done},
                    yes_label=_("Yes, adjust quantities and proceed"),
                    no_label=_("No, review data first"),
                )

            wo = finished_move.workorder_id
            if wo and quantity_done and wo.qty_produced != quantity_done:
                return self._launch_qty_warning(
                    production,
                    _(
                        "Work Order vs Manufacturing Order quantity"
                        " mismatch detected:\n\n"
                        "• Work Orders report %(wo_qty)s units produced.\n"
                        "• Manufacturing Order finished moves report"
                        " %(mo_qty)s units produced.\n\n"
                        "If you choose 'Yes', the system will:\n"
                        "1. Set 'Quantity Producing' to match 'Quantity"
                        " Done'.\n"
                        "2. Update all related Work Orders' 'Quantity"
                        " Producing' and 'Quantity Produced'.\n"
                        "3. Continue marking the Manufacturing Order as"
                        " done."
                    )
                    % {"wo_qty": wo.qty_produced, "mo_qty": quantity_done},
                    yes_label=_("Yes, adjust quantities and proceed"),
                    no_label=_("No, review data first"),
                )

        res = super().button_mark_done()

        for production in self:
            if production.qty_produced > production.product_qty:
                production.product_qty = production.qty_produced

            backorders = self.env["mrp.production"].search(
                [
                    ("procurement_group_id", "=", production.procurement_group_id.id),
                    ("id", "!=", production.id),
                    ("state", "!=", "done"),
                ]
            )
            for backorder in backorders:
                backorder._compute_last_manufactured_lot()
                if (
                    backorder.last_manufactured_lot
                    and backorder.product_id.tracking == "serial"
                ):
                    backorder._auto_generate_finished_serials()

        return res

    @staticmethod
    def _is_wo_auto_picked(move):
        return bool(
            move.manual_consumption
            and move.picked
            and move.workorder_id
            and move.workorder_id.state == "done"
        )

    def _set_qty_producing(self, pick_manual_consumption_moves=True):
        serial_productions = self.filtered(lambda p: p.product_id.tracking == "serial")
        other_productions = self - serial_productions

        if other_productions:
            for production in other_productions:
                production.move_raw_ids.filtered(self._is_wo_auto_picked).write(
                    {"picked": False}
                )
            return super(MrpProduction, other_productions)._set_qty_producing(
                pick_manual_consumption_moves
            )

        for production in serial_productions:
            is_waiting = (
                production.warehouse_id.manufacture_steps != "mrp_one_step"
                and production.picking_ids.filtered(
                    lambda p, prod=production: (
                        p.picking_type_id == prod.warehouse_id.pbm_type_id
                        and p.state not in ("done", "cancel")
                    )
                )
            )

            moves = production.move_raw_ids.filtered(
                lambda m, iw=is_waiting: not iw or m.product_id.tracking == "none"
            ) | production.move_finished_ids.filtered(
                lambda m, prod=production: (
                    m.product_id != prod.product_id or m.product_id.tracking == "serial"
                )
            )

            for move in moves:
                if (
                    move.manual_consumption
                    and move.picked
                    and not self._is_wo_auto_picked(move)
                ):
                    continue
                if move.sudo()._should_bypass_set_qty_producing():
                    continue

                new_qty = float_round(
                    (production.qty_producing - production.qty_produced)
                    * move.unit_factor,
                    precision_rounding=move.product_uom.rounding,
                )
                move._set_quantity_done(new_qty)

                if (
                    (not move.manual_consumption or pick_manual_consumption_moves)
                    and move.quantity
                    and (
                        move.product_id != production.product_id
                        or not move.production_id
                        or move.product_id.tracking != "serial"
                    )
                ):
                    move.picked = True

    def _split_productions(
        self, amounts=False, cancel_remaining_qty=False, set_consumed_qty=False
    ):
        all_productions = super()._split_productions(
            amounts=amounts,
            cancel_remaining_qty=cancel_remaining_qty,
            set_consumed_qty=set_consumed_qty,
        )
        for production in (all_productions - self).filtered(
            lambda p: p.product_id.tracking == "serial" and p.state in ACTIVE_STATES
        ):
            production.with_context(skip_qty_producing_sync=True).write(
                {"qty_producing": production.product_qty}
            )
            production._auto_generate_finished_serials()
        return all_productions

    def action_assign(self):
        for production in self:
            raw_moves = production.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            if not raw_moves:
                continue

            qty_producing = production.qty_producing
            product_qty = production.product_qty

            if not qty_producing or not product_qty:
                raw_moves._action_assign()
                continue

            for move in raw_moves:
                if (
                    move.manual_consumption
                    and move.picked
                    and not self._is_wo_auto_picked(move)
                ):
                    continue

                move.move_line_ids.write({"picked": False})
                move.picked = False
                move._do_unreserve()

                qty_for_producing = float_round(
                    move.product_uom_qty * qty_producing / product_qty,
                    precision_rounding=move.product_uom.rounding,
                )
                if (
                    float_compare(
                        qty_for_producing,
                        0,
                        precision_rounding=move.product_uom.rounding,
                    )
                    > 0
                ):
                    move._action_assign(force_qty=qty_for_producing)
        return True

    def _sync_qty_producing_from_move(self, new_qty):
        self.ensure_one()
        self.write({"qty_producing": new_qty})
        if not self.env.context.get("skip_serial_regeneration"):
            if self.product_id.tracking == "serial":
                self._auto_generate_finished_serials()
            elif self.product_id.tracking == "lot":
                self._auto_regenerate_lot_finished_line()

    def update_quantity_done(self):
        for production in self:
            finished_move = production.move_finished_ids.filtered(
                lambda m, p=production: m.product_id == p.product_id
            )
            if not finished_move:
                continue
            quantity_done = finished_move.quantity
            production.qty_producing = quantity_done
            production._onchange_producing()
            for wo in production.workorder_ids:
                wo.qty_producing = quantity_done
                wo.qty_produced = quantity_done

    def _auto_generate_finished_serials(self):
        self.ensure_one()
        self_ctx = self.with_context(skip_qty_producing_sync=True)

        qty = self_ctx.qty_producing or self_ctx.product_qty
        if not qty or qty <= 0:
            return

        first_lot = self_ctx._increment_serial_number(self_ctx.last_manufactured_lot)
        if not first_lot:
            return

        finished_move = self_ctx.move_finished_ids.filtered(
            lambda m: m.product_id == self_ctx.product_id
        )
        if not finished_move:
            return

        context = {
            "default_product_id": finished_move.product_id.id,
            "default_location_dest_id": finished_move.location_dest_id.id,
            "default_location_id": finished_move.location_id.id,
            "default_tracking": finished_move.product_id.tracking,
            "default_quantity": qty,
            "default_company_id": finished_move.company_id.id,
        }
        move_line_vals = self.env["stock.move"].action_generate_lot_line_vals(
            context=context,
            mode="generate",
            first_lot=first_lot,
            count=int(qty),
            lot_text=None,
        )
        if not move_line_vals:
            return

        MoveLines = self.env["stock.move.line"].with_context(
            skip_qty_producing_sync=True
        )
        finished_move.with_context(skip_qty_producing_sync=True).move_line_ids.unlink()

        for vals in move_line_vals:
            clean_vals = self._flatten_m2o_vals(vals)
            clean_vals["move_id"] = finished_move.id
            MoveLines.create(clean_vals)

    def _auto_regenerate_lot_finished_line(self):
        self.ensure_one()
        self_ctx = self.with_context(skip_qty_producing_sync=True)

        qty = self_ctx.qty_producing
        if not qty or qty <= 0:
            return

        finished_move = self_ctx.move_finished_ids.filtered(
            lambda m: m.product_id == self_ctx.product_id
        )
        if not finished_move:
            return

        finished_move.with_context(skip_qty_producing_sync=True).move_line_ids.unlink()

        self.env["stock.move.line"].with_context(skip_qty_producing_sync=True).create(
            {
                "move_id": finished_move.id,
                "product_id": finished_move.product_id.id,
                "product_uom_id": finished_move.product_uom.id,
                "location_id": finished_move.location_id.id,
                "location_dest_id": finished_move.location_dest_id.id,
                "company_id": finished_move.company_id.id,
                "quantity": qty,
                "lot_name": self_ctx.lot_producing_id.name or "",
            }
        )

    @staticmethod
    def _increment_serial_number(serial):
        if not serial:
            return None
        match = re.search(r"(\d+)(?!.*\d)", serial)
        if not match:
            return serial
        number = match.group(1)
        incremented = str(int(number) + 1).zfill(len(number))
        prefix, *suffix = serial.rsplit(number, 1)
        return prefix + incremented + (suffix[0] if suffix else "")

    @staticmethod
    def _flatten_m2o_vals(vals):
        return {
            key: value["id"] if isinstance(value, dict) and "id" in value else value
            for key, value in vals.items()
        }

    def action_show_finished_move_lines(self):
        self.ensure_one()
        related_productions = self.env["mrp.production"].search(
            [("procurement_group_id", "=", self.procurement_group_id.id)]
        )
        finished_lines = related_productions.mapped("move_finished_ids.move_line_ids")
        return {
            "type": "ir.actions.act_window",
            "name": _("Finished Move Lines"),
            "view_mode": "list",
            "res_model": "stock.move.line",
            "domain": [("id", "in", finished_lines.ids)],
            "context": {"default_procurement_group_id": self.procurement_group_id.id},
        }

    def action_show_finished_move_lines_result_packages(self):
        self.ensure_one()
        packages = self.mapped("move_finished_ids.move_line_ids.result_package_id")
        return {
            "type": "ir.actions.act_window",
            "name": _("Result Packages"),
            "view_mode": "list",
            "res_model": "stock.quant.package",
            "domain": [("id", "in", packages.ids)],
        }

    def _prepare_finished_extra_vals(self):
        if self.product_id.tracking == "lot":
            return {}
        return super()._prepare_finished_extra_vals()

    def _launch_qty_warning(self, production, message, yes_label, no_label):
        return {
            "name": _("Quantity Discrepancy Warning"),
            "type": "ir.actions.act_window",
            "res_model": "mrp.production.qty.warning",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_production_id": production.id,
                "default_warning_message": message,
                "default_yes_label": yes_label,
                "default_no_label": no_label,
            },
        }
