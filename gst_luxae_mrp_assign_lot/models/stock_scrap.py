# (c) Ignacio Ales López - Guadaltech
# (c) 2024 Alfredo de la Fuente - Avanzosc
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, fields, models

from odoo.addons.stock.models.stock_scrap import StockScrap as BaseStockScrap


class StockScrap(models.Model):
    _inherit = "stock.scrap"
    _description = "Stock Scrap"

    def override_mrp_assign_lot_do_scrap(self):
        self._check_company()
        for scrap in self:
            # == BEGIN override change
            scrap.name = (
                "4020" + scrap.production_id.name[3:]
                if scrap.production_id
                else self.env["ir.sequence"].next_by_code("stock.scrap") or _("New")
            )
            # == END override change
            move = self.env["stock.move"].create(scrap._prepare_move_values())
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            scrap.write({"move_id": move.id, "state": "done"})
            scrap.date_done = fields.Datetime.now()
        return True


BaseStockScrap.do_scrap = StockScrap.override_mrp_assign_lot_do_scrap
