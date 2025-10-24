# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    show_set_qty_button = fields.Boolean(
        string="Show set Qty button", compute="_compute_show_qty_button"
    )
    show_clear_qty_button = fields.Boolean(
        string="Show clear Qty Button", compute="_compute_show_qty_button"
    )

    @api.depends("move_raw_ids.should_consume_qty", "move_raw_ids.quantity_done")
    def _compute_show_qty_button(self):
        for mrp in self:
            show_set_qty_button = False
            show_clear_qty_button = False
            moves = mrp.move_raw_ids.filtered(lambda x: x.state == "assigned")
            for move in moves:
                if (
                    move.should_consume_qty > 0
                    and move.quantity_done == 0
                    and float_is_zero(
                        move.quantity_done, precision_rounding=move.product_uom.rounding
                    )
                    and not float_is_zero(
                        move.should_consume_qty,
                        precision_rounding=move.product_uom.rounding,
                    )
                ):
                    show_set_qty_button = True
                if (
                    move.should_consume_qty > 0
                    and move.quantity_done > 0
                    and not float_is_zero(
                        move.quantity_done, precision_rounding=move.product_uom.rounding
                    )
                    and not float_is_zero(
                        move.should_consume_qty,
                        precision_rounding=move.product_uom.rounding,
                    )
                ):
                    show_clear_qty_button = True
            mrp.show_set_qty_button = show_set_qty_button
            mrp.show_clear_qty_button = show_clear_qty_button

    def action_set_quantities_to_should_consume(self):
        moves = self.move_raw_ids.filtered(lambda x: x.state == "assigned")
        for move in moves:
            if (
                move.should_consume_qty > 0
                and move.quantity_done == 0
                and float_is_zero(
                    move.quantity_done, precision_rounding=move.product_uom.rounding
                )
                and not float_is_zero(
                    move.should_consume_qty,
                    precision_rounding=move.product_uom.rounding,
                )
            ):
                move.quantity_done = move.should_consume_qty

    def action_clear_quantities_to_zero(self):
        my_moves = self.env["stock.move"]
        moves = self.move_raw_ids.filtered(lambda x: x.state == "assigned")
        for move in moves:
            if (
                move.should_consume_qty > 0
                and move.quantity_done > 0
                and not float_is_zero(
                    move.quantity_done, precision_rounding=move.product_uom.rounding
                )
                and not float_is_zero(
                    move.should_consume_qty,
                    precision_rounding=move.product_uom.rounding,
                )
            ):
                my_moves += move
        if my_moves:
            my_moves._clear_quantities_to_zero()

    def action_assign(self):
        res = super().action_assign()
        self.action_clear_quantities_to_zero()
        self.action_set_quantities_to_should_consume()
        return res
