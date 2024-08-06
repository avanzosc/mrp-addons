# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("same_subproduct", False):
            vals_list[0]["name"] = "TEMP - 001"
        return super(StockLot, self.with_context(mail_create_nosubscribe=True)).create(
            vals_list
        )
