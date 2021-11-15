# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    post_visible = fields.Boolean(
        string="Allowed to Post Inventory",
        compute="_compute_post_visible",
        help="Technical field to check when we can post")

    @api.depends("finished_workorder_line_ids.qty_done")
    def _compute_post_visible(self):
        for order in self:
            order.post_visible = any(
                (x.quantity_done > 0 and x.state not in ['done', 'cancel'])
                for x in order.move_finished_ids)

    def post_inventory(self):
        for order in self:
            moves_not_to_do = order.move_raw_ids.filtered(
                lambda x: x.state == "done")
            moves_to_do = order.move_raw_ids.filtered(
                lambda x: x.state not in ("done", "cancel"))
            for move in moves_to_do.filtered(
                    lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            # MRP do not merge move, catch the result of _action_done in order
            # to get extra moves.
            moves_to_do = moves_to_do._action_done()
            moves_to_do = (
                order.move_raw_ids.filtered(lambda x: x.state == 'done') -
                moves_not_to_do)
            # order._cal_price(moves_to_do)
            moves_to_finish = order.move_finished_ids.filtered(
                lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish = moves_to_finish._action_done()
            order.raw_workorder_line_ids.unlink()
            order.finished_workorder_line_ids.unlink()
            order.move_raw_ids._action_assign()
            order._refresh_wo_lines()
            consume_move_lines = moves_to_do.mapped("move_line_ids")
            for moveline in moves_to_finish.mapped("move_line_ids"):
                if (moveline.move_id.has_tracking != "none" and
                        moveline.product_id == order.product_id or
                        moveline.lot_id in consume_move_lines.mapped(
                            "lot_produced_ids")):
                    if any([not ml.lot_produced_ids for ml in
                            consume_move_lines]):
                        raise UserError(
                            _("You can not consume without telling for which "
                              "lot you consumed it"))
                    # Link all movelines in the consumed with same
                    # lot_produced_ids false or the correct lot_produced_ids
                    filtered_lines = consume_move_lines.filtered(
                        lambda ml: moveline.lot_id in ml.lot_produced_ids)
                    moveline.write({
                        "consume_line_ids": [
                            (6, 0, [x for x in filtered_lines.ids])]})
                else:
                    # Link with everything
                    moveline.write({
                        "consume_line_ids": [
                            (6, 0, [x for x in consume_move_lines.ids])]})
        return True
