from odoo import models


class UomUom(models.Model):
    _inherit = "uom.uom"

    def _compute_price(self, price, to_unit):
        self.ensure_one()

        # Establecer el atributo rounding a 0.001
        self.rounding = 0.001
        to_unit.rounding = 0.001

        if not self or not price or not to_unit or self == to_unit:
            return price
        if self.category_id.id != to_unit.category_id.id:
            return price

        amount = price * self.factor
        if to_unit:
            amount = amount / to_unit.factor
        return amount
