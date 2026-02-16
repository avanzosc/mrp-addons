# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_cancel_reverse_internal_pickings(self):
        wiz_obj = self.env["wiz.reverse.internal.picking.from.of"]
        wizard = wiz_obj.create(self._catch_values_for_reverse_internal_pickings())
        context = self.env.context.copy()
        return {
            "name": _("Reverse Internal Picking From OF"),
            "type": "ir.actions.act_window",
            "res_model": "wiz.reverse.internal.picking.from.of",
            "view_type": "form",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
            "context": context,
        }

    def _catch_picking_info_for_reverse(self, done_picking):
        vals = super()._catch_picking_info_for_reverse(done_picking)
        if done_picking.claim_id:
            vals["claim_id"] = done_picking.claim_id.id
        return vals
