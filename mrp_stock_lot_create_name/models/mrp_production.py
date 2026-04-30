# (c) 2024 Alfredo de la Fuente - Avanzosc
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    _description = "Mrp Production"

    def action_generate_serial(self):
        self.ensure_one()
        if self.product_id.tracking != "lot":
            return super().action_generate_serial()
        if not self.lot_producing_id:
            self.lot_producing_id = self.env["stock.lot"].create(
                self._prepare_personalized_stock_lot_values()
            )

    def _prepare_personalized_stock_lot_values(self):
        self.ensure_one()
        if self.picking_type_id.lot_code:
            name = self.picking_type_id.lot_code + self.name[4:]
        else:
            name = self.name[4:]
        return {
            "product_id": self.product_id.id,
            "company_id": self.company_id.id,
            "name": name,
        }

    def button_mark_done(self):
        production_lot = self.env["stock.lot"]
        for production in self:
            for move in production.move_raw_ids:
                lines = move.move_line_ids.filtered(lambda line: line.quantity == 0)
                total = move.product_uom_qty - move.quantity
                if lines:
                    qty_per_line = total // len(lines)
                    remainder = total % len(lines)

                    for i, ml in enumerate(lines):
                        ml.quantity = qty_per_line + (1 if i < remainder else 0)
            vals = {"qty_producing": production.product_qty}
            if production.picking_type_id.lot_code:
                name = production.picking_type_id.lot_code + production.name[4:]
            else:
                name = production.name[4:]
            lot_found = production_lot.search(
                [
                    ("product_id", "=", production.product_id.id),
                    ("name", "=", name),
                    ("company_id", "=", production.company_id.id),
                ],
                limit=1,
            )
            if production.product_id.tracking == "lot" and (
                not production.lot_producing_id
                or production.lot_producing_id.name != name
            ):
                if lot_found:
                    vals["lot_producing_id"] = lot_found.id
                else:
                    lot = production_lot.create(
                        production._prepare_personalized_stock_lot_values()
                    )
                    vals["lot_producing_id"] = lot.id
            production.write(vals)
        return super().button_mark_done()
