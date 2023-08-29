# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    post_visible = fields.Boolean(
        string="Allowed to Post Inventory",
        compute="_compute_post_visible",
        help="Technical field to check when we can post",
    )

    @api.depends("state")
    def _compute_post_visible(self):
        for workorder in self:
            pending_raw_moves = workorder.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            has_done_moves = any([m.quantity_done for m in pending_raw_moves])
            workorder.post_visible = has_done_moves and workorder.state == "done"

    def post_inventory(self):
        self.ensure_one()
        return self.production_id.button_mark_done()
