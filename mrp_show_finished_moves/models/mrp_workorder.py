# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def action_show_finished_move_lines_result_packages(self):
        self.ensure_one()
        finished_lines_packages = self.mapped(
            "move_finished_ids.move_line_ids.result_package_id"
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Result Packages",
            "view_mode": "tree",
            "res_model": "stock.quant.package",
            "domain": [("id", "in", finished_lines_packages.ids)],
        }
