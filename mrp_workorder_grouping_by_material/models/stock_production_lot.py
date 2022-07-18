# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    product_life_alert = fields.Boolean(
        string="Product Life Alert", compute="_compute_product_life_alert"
    )

    @api.depends("alert_date")
    def _compute_product_life_alert(self):
        current_date = fields.Datetime.now()
        for lot in self:
            lot.product_life_alert = (
                lot.alert_date and lot.alert_date <= current_date or False
            )
