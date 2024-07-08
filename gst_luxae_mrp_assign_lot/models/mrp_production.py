# (c) Ignacio Ales López - Guadaltech
# (c) 2024 Alfredo de la Fuente - Avanzosc
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    _description = "Mrp Production"

    def action_generate_serial(self):
        self.ensure_one()
        if self.product_id.tracking != "lot":
            return super(MrpProduction, self).action_generate_serial()
        if not self.lot_producing_id:
            self.lot_producing_id = self.env["stock.lot"].create(
                self._prepare_personalized_stock_lot_values())

    def _prepare_personalized_stock_lot_values(self):
        self.ensure_one()
        name = "3601" + self.name[4:]
        return {
            "product_id": self.product_id.id,
            "company_id": self.company_id.id,
            "name": name,
        }

    def button_mark_done(self):
        production_lot = self.env["stock.lot"]
        for production in self:
            for move_line in production.mapped("move_raw_ids.move_line_ids").filtered(
                lambda _move: _move.qty_done == 0.0
            ):
                move_line.qty_done = move_line.reserved_uom_qty
            vals = {"qty_producing": production.product_qty}
            name = "3601" + production.name[4:]
            lot_found = production_lot.search(
                [("product_id", "=", self.product_id.id),
                 ("name", "=", name),
                 ("company_id", "=", self.company_id.id)], limit=1)
            if (production.product_id.tracking == "lot" and
                (not production.lot_producing_id or
                    production.lot_producing_id.name != name)
            ):
                if lot_found:
                    vals["lot_producing_id"] = lot_found.id
                else:
                    lot = production_lot.create(
                        production._prepare_personalized_stock_lot_values())
                    vals["lot_producing_id"] = lot.id

            production.write(vals)
        return super().button_mark_done()

    # def action_confirm(self):
    #     for production in self:
    #         production.write({
    #             "qty_producing": production.product_qty
    #             })
    #     return super(MrpProduction, self).action_confirm()
