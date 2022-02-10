# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .mrp_workorder import print_report
from odoo import models


class MrpWorkorderNestLine(models.Model):
    _inherit = "mrp.workorder.nest.line"

    def print_report(self):
        records = self.filtered(lambda r: r.workorder_id.worksheet)
        return print_report(records,
                            "mrp_workorder_data_worksheet_header."
                            "mrp_workorder_nest_line_worksheet_report")

    def get_worksheets(self):
        pdf = self.print_report()
        if not pdf or not self.env.context.get("print", False):
            return super().get_worksheets()
        return pdf
