# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def show_worksheets(self):
        self.ensure_one()
        worksheets = self.mapped(
            "finished_workorder_line_ids").get_worksheets()
        if not worksheets:
            return
        wizard = self.env["binary.container"].create({
            "binary_field": (
                worksheets[0] if isinstance(worksheets, list) else worksheets),
        })
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update({
            "name": _("Worksheets"),
            "res_id": wizard.id,
        })
        return action_dict
