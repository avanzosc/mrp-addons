# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    last_version = fields.Char(
        string="Last Version",
        compute="_compute_last_version",
        store=True,
    )

    @api.depends("bom_line_ids", "bom_line_ids.version")
    def _compute_last_version(self):
        for product in self:
            if product.bom_line_ids:
                product.last_version = max(
                    product.bom_line_ids, key=lambda x: int(x.version)
                ).version
            else:
                product.last_version = "00"
