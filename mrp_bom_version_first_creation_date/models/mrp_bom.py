# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    first_creation_date = fields.Datetime(
        compute="_compute_first_creation_date",
        store=True,
    )

    @api.depends(
        "create_date", "previous_bom_id", "previous_bom_id.first_creation_date"
    )
    def _compute_first_creation_date(self):
        for bom in self.sorted(key=lambda b: b.id):
            if not bom.previous_bom_id:
                bom.first_creation_date = bom.create_date
            else:
                if bom.id != bom.previous_bom_id.id:
                    bom.first_creation_date = bom.previous_bom_id.first_creation_date
