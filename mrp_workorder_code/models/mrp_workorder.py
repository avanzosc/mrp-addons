# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    code = fields.Char(
        compute="_compute_code",
        store=True,
        copy=False,
    )

    @api.depends("production_id", "production_id.name", "sequence")
    def _compute_code(self):
        for workorder in self:
            workorder.code = "%(production_name)s-%(sequence)s" % {
                "production_name": workorder.production_id.name or "",
                "sequence": workorder.sequence,
            }
