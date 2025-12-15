# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    last_manufactured_lot = fields.Char(
        compute="_compute_last_manufactured_lot",
    )

    @api.depends("product_id")
    def _compute_last_manufactured_lot(self):
        MoveLine = self.env["stock.move.line"]
        for production in self:
            lot = MoveLine.search(
                [
                    ("product_id", "=", production.product_id.id),
                    ("lot_id", "!=", False),
                    ("state", "=", "done"),
                ],
                order="date desc",
                limit=1,
            )

            production.last_manufactured_lot = lot.lot_id.name if lot else False

    def _increment_serial_number(self, serial):
        if not serial:
            return None
        match = re.search(r"(\d+)(?!.*\d)", serial)
        if not match:
            return serial
        last_number = int(match.group(1))
        incremented_number = last_number + 1
        parts = serial.rsplit(match.group(1), 1)
        new_serial = (
            parts[0]
            + str(incremented_number).zfill(len(match.group(1)))
            + (parts[1] if len(parts) > 1 else "")
        )
        return new_serial

    def _update_move_next_serial(self):
        for production in self:
            if production.last_manufactured_lot:
                next_serial = self._increment_serial_number(
                    production.last_manufactured_lot
                )
                if next_serial:
                    moves_to_update = production.move_finished_ids.filtered(
                        lambda m: m.product_id == production.product_id
                    )
                    moves_to_update.write({"next_serial": next_serial})

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

    def action_show_finished_move_lines_result_packages(self):
        self.ensure_one()
        finished_lines_packages = self.mapped(
            "move_finished_ids.move_line_ids.result_package_id"
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Result Packages",
            "view_mode": "tree",
            "res_model": "stock.quant.package",
            "domain": [("id", "in", finished_lines_packages.ids)],
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

    def button_mark_done(self):
        for production in self:
            finished_move = production.move_finished_ids.filtered(
                lambda m: m.product_id.id == production.product_id.id
            )
            if finished_move:
                quantity_done = finished_move.quantity_done
                if quantity_done != production.qty_producing and quantity_done != 0:
                    return self._launch_qty_warning(
                        production,
                        _(
                            "Producing vs Done quantity mismatch detected:\n\n"
                            "• Manufacturing Order reports %(planned)s units producing.\n"
                            "• Manufacturing Order finished moves report %(actual)s units\n"
                            "  produced.\n\n"
                            "If you choose 'Yes', the system will:\n"
                            "1. Set 'Quantity Producing' to match 'Quantity Done'.\n"
                            "2. Update all related WOs' 'Quantity Producing' and\n"
                            "   'Quantity Produced' to match 'Quantity Done'.\n"
                            "3. Continue marking the Manufacturing Order as done."
                        )
                        % {
                            "planned": production.qty_producing,
                            "actual": quantity_done,
                        },
                        yes_label=_("Yes, adjust quantities and proceed"),
                        no_label=_("No, review data first"),
                    )
                if finished_move.workorder_id:
                    qty_produced_wo = finished_move.workorder_id.qty_produced
                    if qty_produced_wo != quantity_done and quantity_done != 0:
                        return self._launch_qty_warning(
                            production,
                            _(
                                "Work Order vs Manufacturing Order quantity "
                                "mismatch detected:\n\n"
                                "• Work Orders report %(wo_qty)s units produced.\n"
                                "• Manufacturing Order finished moves report %(mo_qty)s units\n"
                                "  produced.\n\n"
                                "If you choose 'Yes', the system will:\n"
                                "1. Set 'Quantity Producing' to match 'Quantity Done'.\n"
                                "2. Update all related Work Orders' 'Quantity Producing' and\n"
                                "   'Quantity Produced' to match 'Quantity Done'.\n"
                                "3. Continue marking the Manufacturing Order as done."
                            )
                            % {
                                "wo_qty": qty_produced_wo,
                                "mo_qty": quantity_done,
                            },
                            yes_label=_("Yes, adjust quantities and proceed"),
                            no_label=_("No, review data first"),
                        )
        return super().button_mark_done()

    def _launch_qty_warning(self, production, message, yes_label, no_label):
        """Launches the generic quantity warning wizard with context-specific text."""
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

    def update_quantity_done(self):
        for production in self:
            finished_move = production.move_finished_ids.filtered(
                lambda m: m.product_id == production.product_id
            )
            if finished_move:
                quantity_done = finished_move.quantity_done
                production.qty_producing = quantity_done
                production._onchange_producing()
                for wo in production.workorder_ids:
                    wo.qty_producing = quantity_done
                    wo.qty_produced = quantity_done

    @api.model
    def create(self, vals):
        production = super().create(vals)
        if production.last_manufactured_lot:
            production._update_move_next_serial()
        return production

    def write(self, vals):
        res = super().write(vals)
        if "lot_producing_id" in vals:
            for production in self:
                new_name = (
                    production.lot_producing_id.name
                    if production.lot_producing_id
                    else False
                )
                for move in production.move_finished_ids:
                    if (
                        move.product_id == production.product_id
                        and not move.raw_material_production_id
                        and move.product_id.tracking == "lot"
                    ):
                        ml_cmds = []
                        for ml in move.move_line_ids:
                            if ml.id:
                                ml_cmds.append((1, ml.id, {"lot_name": new_name}))
                            else:
                                ml_cmds.append(
                                    (
                                        0,
                                        0,
                                        {
                                            "product_id": ml.product_id.id,
                                            "qty_done": ml.qty_done,
                                            "lot_name": new_name,
                                        },
                                    )
                                )
                        move.move_line_ids = ml_cmds
                if "last_manufactured_lot" in vals:
                    production._update_move_next_serial()
        return res


class MrpProductionQtyWarning(models.TransientModel):
    _name = "mrp.production.qty.warning"
    _description = "Inconsistency in Quants Warning"

    production_id = fields.Many2one("mrp.production")
    warning_message = fields.Text(readonly=True)
    yes_label = fields.Char(default="Yes")
    no_label = fields.Char(default="No")

    def action_yes(self):
        self.production_id.update_quantity_done()
        return self.production_id.button_mark_done()

    def action_no(self):
        return {"type": "ir.actions.act_window_close"}
