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

    def _catch_values_for_reverse_internal_pickings(self):
        production_obj = self.env["mrp.production"]
        vals = {"production_id": self.id}
        cond = [("procurement_group_id", "=", self.procurement_group_id.id)]
        same_procurement_group_productions = production_obj.search(cond)
        wizard_lines = []
        done_pickings = same_procurement_group_productions.mapped(
            "picking_ids"
        ).filtered(lambda p: p.state == "done" and p.picking_type_id.code == "internal")
        for done_picking in done_pickings:
            wizard_lines.append(
                (0, 0, self._catch_picking_info_for_reverse(done_picking))
            )
        if len(same_procurement_group_productions) == 1:
            vals["more_than_one_production"] = False
            vals["wizard_lines_auto"] = wizard_lines
        else:
            same_procurement_group_productions -= self
            vals["other_productions"] = [(6, 0, same_procurement_group_productions.ids)]
            vals["more_than_one_production"] = True
            vals["wizard_lines_manual"] = wizard_lines
        return vals

    def _catch_picking_info_for_reverse(self, done_picking):
        vals = {"picking_id": done_picking.id}
        return vals
