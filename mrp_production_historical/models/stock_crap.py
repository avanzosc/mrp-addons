# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def do_scrap(self):
        self._check_company()
        for scrap in self.filtered(lambda x: x.production_id):
            move = scrap.production_id.move_raw_ids.filtered(
                lambda x: x.product_id == scrap.product_id
                and x.state not in ("done", "cancel")
            )
            if not move:
                move = scrap.production_id.move_finished_ids.filtered(
                    lambda x: x.product_id == scrap.product_id and x.state == "done"
                )
            if move:
                scrap.create_mrp_production_historical(move)
        return super(StockScrap, self.with_context(from_scrap=True)).do_scrap()

    def create_mrp_production_historical(self, move):
        vals = self.get_values_for_create_mrp_production_historical(move)
        historical = (
            self.env["mrp.production.historical"]
            .with_context(scrap_history=True)
            .create(vals)
        )
        return historical

    def get_values_for_create_mrp_production_historical(self, move):
        vals = {
            "production_id": self.production_id.id,
            "historical_date": fields.Datetime.now(),
            "type": "scraped",
            "user_id": self.env.user.id,
            "product_id": self.product_id.id,
            "programed_qty": move.product_uom_qty,
            "scraped_qty": self.scrap_qty,
        }
        return vals
