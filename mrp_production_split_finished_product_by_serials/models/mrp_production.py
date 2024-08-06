# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    initial_product_qty = fields.Float(
        compute="_compute_total_produced_qty",
        string="Initial Quantity To Produce",
        digits="Product Unit of Measure",
    )
    total_produced_qty = fields.Float(
        compute="_compute_total_produced_qty",
        string="Total Quantity Produced",
        digits="Product Unit of Measure",
    )
    serial_lot_name = fields.Char(
        copy=False,
    )

    @api.onchange("lot_producing_id")
    def _onchange_lot_producing(self):
        res = super()._onchange_lot_producing()
        self.serial_lot_name = self.lot_producing_id.name
        if res is not True:
            return res

    @api.depends(
        "procurement_group_id.mrp_production_ids",
        "workorder_ids.state",
        "move_finished_ids",
        "move_finished_ids.quantity_done",
        "procurement_group_id.mrp_production_ids.workorder_ids.state",
        "procurement_group_id.mrp_production_ids.move_finished_ids",
        "procurement_group_id.mrp_production_ids.move_finished_ids.quantity_done",
    )
    def _compute_total_produced_qty(self):
        for production in self:
            grouped_productions = production.mapped(
                "procurement_group_id.mrp_production_ids"
            )
            production.total_produced_qty = sum(
                grouped_productions.mapped("qty_produced")
            )
            production.initial_product_qty = sum(
                grouped_productions.mapped("product_qty")
            )

    def _get_backorder_mo_vals(self):
        values = super()._get_backorder_mo_vals()
        values.update(
            {
                "serial_lot_name": self.serial_lot_name,
            }
        )
        return values

    def _split_productions(
        self, amounts=False, cancel_remaining_qty=False, set_consumed_qty=False
    ):
        productions = super()._split_productions(
            amounts=amounts,
            cancel_remaining_qty=cancel_remaining_qty,
            set_consumed_qty=set_consumed_qty,
        )
        for production in productions.filtered(
            lambda b: b.product_id.tracking == "serial"
        ):
            production.qty_producing = production.product_qty
        return productions

    def _get_lot_name(self, number=1):
        self.ensure_one()
        number = int(number)
        lot_counter_length = max(len(str(int(self.initial_product_qty))), 3)
        lot_name = self.serial_lot_name
        base_lot_name = (
            lot_name[: -(lot_counter_length + 1)] if "x" in lot_name else lot_name
        )
        new_lot_name = "{}x{}".format(
            base_lot_name, str(number).zfill(lot_counter_length)
        )
        return new_lot_name

    def action_generate_serial(self):
        if (
            self.product_tracking == "serial"
            and self.state not in ("done", "cancel")
            and not self.serial_lot_name
        ):
            raise exceptions.UserError(_("You must introduce the serial lot name."))
        if self.serial_lot_name:
            lot_name = self._get_lot_name(self.total_produced_qty + 1)
            return super(
                MrpProduction,
                self.with_context(
                    default_name=lot_name, qty_twith_serial=self.qty_producing
                ),
            ).action_generate_serial()

    def _set_qty_producing(self):
        if self.product_id.tracking and self.product_id.tracking == "serial":
            return super(
                MrpProduction, self.with_context(qty_twith_serial=self.qty_producing)
            )._set_qty_producing()
        else:
            return super()._set_qty_producing()

    def button_mark_done(self):
        if self.product_tracking == "serial":
            if not self.lot_producing_id:
                lot_name = self._get_lot_name(self.total_produced_qty + 1)
                self.lot_producing_id = self.env["stock.lot"].create(
                    {
                        "name": lot_name,
                        "product_id": self.product_id.id,
                        "company_id": self.company_id.id,
                    }
                )
            return super(
                MrpProduction, self.with_context(with_tracking_serial=True)
            ).button_mark_done()
        else:
            return super().button_mark_done()

    def _post_inventory(self, cancel_backorder=False):
        for production in self.filtered(lambda p: p.product_id.tracking == "serial"):
            production.create_lot_for_tracking_serial()
        result = super()._post_inventory(cancel_backorder=cancel_backorder)
        return result

    def create_lot_for_tracking_serial(self):
        self.ensure_one()
        moves = self.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id
        )
        lot_obj = self.env["stock.lot"]
        offset = self.total_produced_qty or 0
        cont = offset
        for move in moves:
            qty_done = move.product_uom_qty + offset
            move_lines_commands = []
            for move_line in move.move_line_ids:
                cont += 1
                move_lines_commands.append(
                    (
                        1,
                        move_line.id,
                        {
                            "qty_done": 1.0,
                        },
                    )
                )
            while cont < qty_done:
                cont += 1
                lot_name = self._get_lot_name(cont)
                lot = lot_obj.search([("name", "=", lot_name)])
                if not lot:
                    lot = lot_obj.create(
                        {
                            "name": lot_name,
                            "product_id": move.product_id.id,
                            "company_id": self.company_id.id,
                        }
                    )
                move_line_vals = move._prepare_move_line_vals(quantity=0)
                move_line_vals["lot_id"] = lot.id
                move_line_vals["lot_name"] = lot.name
                move_line_vals["product_uom_id"] = move.product_id.uom_id.id
                move_line_vals["qty_done"] = 1
                move_lines_commands.append((0, 0, move_line_vals))
            move.with_context(bypass_reservation_update=True).write(
                {
                    "move_line_ids": move_lines_commands,
                }
            )
