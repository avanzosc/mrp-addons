# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("move_raw_ids", "state", "move_raw_ids.product_uom_qty")
    def _compute_unreserve_visible(self):
        result = super(MrpProduction, self)._compute_unreserve_visible()
        for order in self:
            already_reserved = (
                order.state not in
                ("done", "cancel") and order.mapped(
                    "move_raw_ids.move_line_ids"))
            order.unreserve_visible = True if already_reserved else False
        return result
