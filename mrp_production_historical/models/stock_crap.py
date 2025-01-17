# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def do_scrap(self):
        self._check_company()
        for scrap in self.filtered(lambda x: x.production_id):
            scrap.create_mrp_production_historical()
        return super(StockScrap, self.with_context(from_scrap=True)).do_scrap()

    def create_mrp_production_historical(self):
        vals = self.get_values_for_create_mrp_production_historical()
        historical = (
            self.env["mrp.production.historical"]
            .with_context(scrap_history=True)
            .create(vals)
        )
        return historical

    def get_values_for_create_mrp_production_historical(self):
        vals = {
            "production_id": self.production_id.id,
            "historical_date": fields.Datetime.now(),
            "type": "scraped",
            "user_id": self.env.user.id,
            "product_id": self.product_id.id,
            "scraped_qty": self.scrap_qty,
        }

        if self.production_id.product_id == self.product_id:
            vals["programed_qty"] = self.production_id.product_qty
        else:
            line = self.production_id.move_raw_ids.filtered(
                lambda line: line.product_id == self.product_id
            )
            if line:
                vals["programed_qty"] = line[0].product_uom_qty
            else:
                vals["programed_qty"] = 0

        return vals
