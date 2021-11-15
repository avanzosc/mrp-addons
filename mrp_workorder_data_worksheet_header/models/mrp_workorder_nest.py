# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpWorkorderNest(models.Model):
    _inherit = "mrp.workorder.nest"

    def get_worksheets(self):
        pdf = self.mapped("nested_line_ids").get_worksheets()
        if not pdf or not self.env.context.get("print", False):
            return super().get_worksheets()
        return pdf
