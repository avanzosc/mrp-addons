# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    historical_ids = fields.One2many(
        string="Historical",
        comodel_name="mrp.production.historical",
        inverse_name="bom_id",
        copy=False,
    )

    def _copy_bom(self):
        new_bom = super(
            MrpBom, self.with_context(no_create_historical=True)
        )._copy_bom()
        return new_bom
