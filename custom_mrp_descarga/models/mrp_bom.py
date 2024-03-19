# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    quartering = fields.Boolean(
        string="Quartering",
        compute="_compute_quartering",
        store=True)
    no_duplicate_lines = fields.Boolean(
        string="No Duplicate Lines",
        default=False)

    @api.depends("category_id")
    def _compute_quartering(self):
        for line in self:
            line.quartering = False
            try:
                quartering = (
                    self.env.ref("custom_mrp_descarga.quartering_category"))
                if line.category_id == quartering:
                    line.quartering = True
            except Exception:
                line.quartering = False
