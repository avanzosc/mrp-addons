# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"
    _order = "customer_id desc"

    customer_id = fields.Many2one(
        string="Lot customer", comodel_name="res.partner",
        related="lot_id.customer_id", store=True, copy=False)

    def _gather(self, product_id, location_id, lot_id=None, package_id=None,
                owner_id=None, strict=False):
        quants = super(StockQuant, self)._gather(
            product_id, location_id, lot_id=lot_id, package_id=package_id,
            owner_id=owner_id, strict=strict)
        if (quants and "customer" in self.env.context and
                self.env.context.get("customer", False)):
            my_quants = self.env["stock.quant"]
            customer = self.env.context.get("customer")
            for quant in quants.filtered(
                lambda x: x.lot_id.customer_id and
                    x.lot_id.customer_id == customer):
                if quant not in my_quants:
                    my_quants += quant
            for quant in quants.filtered(lambda x: not x.lot_id.customer_id):
                if quant not in my_quants:
                    my_quants += quant
            if my_quants:
                quants = my_quants
        return quants
