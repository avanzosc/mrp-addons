# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.onchange("bom_revision", "product_tmpl_id", "product_id")
    def onchange_reference(self):
        tmpl = (
            self.product_tmpl_id.default_code
            if self.product_tmpl_id.default_code
            else ""
        )
        va = self.product_id.default_code if (self.product_id.default_code) else ""
        self.code = "{} {} {}".format(va, tmpl, self.bom_revision)
