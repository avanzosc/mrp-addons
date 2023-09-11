# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    show_final_lots = fields.Boolean(compute="_compute_show_lots")
    unreserve_visible = fields.Boolean(
        string="Allowed to Unreserve Inventory",
        compute="_compute_unreserve_visible",
        help="Technical field to check when we can unreserve",
    )
    show_check_availability = fields.Boolean(
        compute="_compute_show_check_availability",
        help="Technical field used to compute whether the check availability "
        "button should be shown.",
    )

    @api.depends("product_id.tracking")
    def _compute_show_lots(self):
        for order in self:
            order.show_final_lots = order.product_id.tracking != "none"

    @api.depends("move_raw_ids", "move_raw_ids.mrp_unreserve_visible")
    def _compute_unreserve_visible(self):
        for order in self:
            pending_raw_moves = order.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            order.unreserve_visible = any(
                [m.mrp_unreserve_visible for m in pending_raw_moves]
            )

    def _compute_show_check_availability(self):
        """According to `workorder.show_check_availability`, the
        "check availability" button will be displayed in the form view of a
        work order.
        """
        for workorder in self:
            if workorder.state in ("done", "cancel"):
                workorder.show_check_availability = False
                continue
            workorder.show_check_availability = any(
                move.state in ("waiting", "confirmed", "partially_available")
                and float_compare(
                    move.product_uom_qty,
                    0,
                    precision_rounding=move.product_uom.rounding,
                )
                for move in workorder.move_raw_ids
            )

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
