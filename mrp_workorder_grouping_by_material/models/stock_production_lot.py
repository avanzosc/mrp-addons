# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    product_life_alert = fields.Boolean(
        string="Product Life Alert",
        compute="_compute_product_life_alert",
        search="_search_product_life_alert",
    )

    @api.depends("alert_date")
    def _compute_product_life_alert(self):
        current_date = fields.Datetime.now()
        for lot in self:
            lot.product_life_alert = (
                lot.alert_date and lot.alert_date <= current_date or False
            )

    def _search_product_life_alert(self, operator, value):
        today = fields.Date.context_today(self)
        life_alert_lots = self.search(
            [("alert_date", "!=", False), ("alert_date", "<=", today)]
        )
        if operator == "=" and value:
            return [("id", "in", life_alert_lots.ids)]
        else:
            return [("id", "not in", life_alert_lots.ids)]
