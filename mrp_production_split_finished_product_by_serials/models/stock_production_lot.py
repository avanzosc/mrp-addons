# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model_create_multi
    def create(self, vals_list):
        if "same_subproduct" in self.env.context:
            vals_list[0]['name'] = "TEMP - 001"
        return super(StockProductionLot, self.with_context(
            mail_create_nosubscribe=True)).create(vals_list)
