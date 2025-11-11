# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_cancel(self):
        result = super().action_cancel()
        if self.state == "cancel":
            picking = self.picking_ids.filtered(
                lambda x: x.state == "done" and x.picking_type_id.code == "internal"
            )
            if picking:
                return {
                    "type": "ir.actions.act_window",
                    "name": _("Reverse Internal Picking From OF"),
                    "res_model": "wiz.reverse.internal.picking.from.of",
                    "view_mode": "form",
                    "target": "new",
                    "context": dict(
                        self.env.context,
                        default_picking_id=picking.id,
                    ),
                }
        return result
