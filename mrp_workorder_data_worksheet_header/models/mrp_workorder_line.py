# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models

from .mrp_workorder import print_report


class MrpWorkorderLine(models.Model):
    _inherit = "mrp.workorder.line"

    def print_report(self):
        records = self.filtered(lambda r: r.finished_workorder_id.worksheet)
        return print_report(
            records,
            "mrp_workorder_data_worksheet_header.mrp_workorder_line_worksheet_report",
        )

    def get_worksheets(self):
        pdf = self.print_report()
        if not pdf or not self.env.context.get("print", False):
            return self.filtered("finished_workorder_id.worksheet").mapped(
                "finished_workorder_id.worksheet"
            )
        return pdf

    def show_worksheets(self):
        worksheets = self.get_worksheets()
        if not worksheets:
            return
        wizard = self.env["binary.container"].create(
            {
                "binary_field": (
                    worksheets[0] if isinstance(worksheets, list) else worksheets
                ),
            }
        )
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update(
            {
                "name": _("Worksheets"),
                "res_id": wizard.id,
            }
        )
        return action_dict
