# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MultipleCopy(models.TransientModel):
    _name = "multiple.copy"
    _description = "Wizard to Duplicate Nests"

    copy_number = fields.Integer(string="Number of Copies", default="1")

    def action_make_copies(self):
        nest_ids = self._context.get("active_ids")
        nests = self.env["mrp.workorder.nest"].browse(nest_ids)
        for nest in nests:
            for _i in range(self.copy_number):
                nest.copy()
