# (c) 2024 Alfredo de la Fuente - Avanzosc
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
from odoo.tools import float_is_zero


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

    def _set_personalized_lot_producing(self):
        self.ensure_one()
        if self.product_id.tracking != "lot":
            return
        if self.picking_type_id.lot_code:
            name = self.picking_type_id.lot_code + self.name[4:]
        else:
            name = self.name[4:]
        if self.lot_producing_id and self.lot_producing_id.name == name:
            return
        lot = self.env["stock.lot"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("name", "=", name),
                ("company_id", "=", self.company_id.id),
            ],
            limit=1,
        )
        if not lot:
            lot = self.env["stock.lot"].create(
                self._prepare_personalized_stock_lot_values()
            )
        self.lot_producing_id = lot.id

    def button_mark_done(self):
        for production in self:
            rounding = production.product_uom_id.rounding
            if float_is_zero(production.qty_producing, precision_rounding=rounding):
                production.qty_producing = (
                    production.product_qty - production.qty_produced
                )
                moves_with_qty = production.move_raw_ids.filtered(
                    lambda m: not float_is_zero(
                        m.quantity, precision_rounding=m.product_uom.rounding
                    )
                )
                if not moves_with_qty:
                    production._set_qty_producing()
            production._set_personalized_lot_producing()
        return super().button_mark_done()
