# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# Copyright 2026 Eñaut Alberdi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    use_create_components_lots = fields.Boolean(
        related="production_id.use_create_components_lots"
    )
    show_final_lots = fields.Boolean(compute="_compute_show_lots")
    unreserve_visible = fields.Boolean(
        string="Allowed to Unreserve Inventory",
        compute="_compute_stock_buttons_visibility",
        help="Technical field to check when we can unreserve",
    )
    show_check_availability = fields.Boolean(
        compute="_compute_stock_buttons_visibility",
        help="Technical field used to compute whether the check availability "
        "button should be shown.",
    )

    @api.depends("product_id.tracking")
    def _compute_show_lots(self):
        for order in self:
            order.show_final_lots = order.product_id.tracking != "none"

    @api.depends(
        "state",
        "date_start",
        "move_raw_ids.state",
        "move_raw_ids.product_uom_qty",
        "move_raw_ids.mrp_unreserve_visible",
    )
    def _compute_stock_buttons_visibility(self):
        """Compute both stock action buttons as mutually exclusive."""
        for workorder in self:
            workorder.unreserve_visible = False
            workorder.show_check_availability = False

            if workorder.state in ("done", "cancel") or not workorder.date_start:
                continue

            pending_raw_moves = workorder.move_raw_ids.filtered(
                lambda move: move.state not in ("done", "cancel")
            )

            can_unreserve = any(
                move.mrp_unreserve_visible for move in pending_raw_moves
            )
            if can_unreserve:
                workorder.unreserve_visible = True
                workorder.show_check_availability = False
                continue

            can_check_availability = any(
                move.state in ("waiting", "confirmed", "partially_available")
                and float_compare(
                    move.product_uom_qty,
                    0,
                    precision_rounding=move.product_uom.rounding,
                )
                for move in pending_raw_moves
            )
            if can_check_availability:
                workorder.show_check_availability = True

    def action_assign(self):
        for order in self:
            order.move_raw_ids._action_assign()
        return True

    def do_unreserve(self):
        for order in self:
            order.move_raw_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )._do_unreserve()
        return True

    def button_unreserve(self):
        self.ensure_one()
        self.do_unreserve()
        return True
