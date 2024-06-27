# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    version = fields.Char(string="Version")
    outdate = fields.Boolean(
        string="Out Date",
        compute="_compute_outdate",
        store=True,
    )

    @api.depends("version", "product_id.last_version", "product_id")
    def _compute_outdate(self):
        for line in self:
            if int(line.version) < int(line.product_id.last_version):
                line.outdate = True
            else:
                line.outdate = False

    @api.onchange("product_id")
    def onchange_version(self):
        if self.product_id:
            self.version = self.product_id.last_version
