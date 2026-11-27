# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def _finished_move_lines_action(self, name, res_model, domain):
        return {
            "type": "ir.actions.act_window",
            "name": name,
            "view_mode": "list",
            "res_model": res_model,
            "domain": domain,
        }

    def action_show_finished_move_lines(self):
        self.ensure_one()
        related_productions = self.env["mrp.production"].search(
            [("procurement_group_id", "=", self.production_id.procurement_group_id.id)]
        )
        finished_lines = related_productions.mapped("move_finished_ids.move_line_ids")
        return self._finished_move_lines_action(
            name=_("Finished Move Lines"),
            res_model="stock.move.line",
            domain=[("id", "in", finished_lines.ids)],
        )

    def action_show_finished_move_lines_result_packages(self):
        self.ensure_one()
        packages = self.mapped("move_finished_ids.move_line_ids.result_package_id")
        return self._finished_move_lines_action(
            name=_("Result Packages"),
            res_model="stock.quant.package",
            domain=[("id", "in", packages.ids)],
        )
