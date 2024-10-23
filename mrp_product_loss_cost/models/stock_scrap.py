# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    scrap_unit_cost = fields.Float(digits="Product Price", copy=False)
    scrap_cost = fields.Float(digits="Product Price", copy=False)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id and self.product_id.standard_price:
            self.scrap_unit_cost = self.product_id.standard_price
        return super()._onchange_product_id()

    @api.onchange("lot_id")
    def _onchange_serial_number(self):
        result = super()._onchange_serial_number()
        if self.lot_id and self.lot_id.purchase_price:
            self.scrap_unit_cost = self.lot_id.purchase_price
        return result

    @api.onchange("scrap_unit_cost", "scrap_qty")
    def _onchange_price_unit_cost(self):
        self.scrap_cost = self.scrap_unit_cost * self.scrap_qty

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "scrap_unit_cost" not in vals:
                vals = self._calculate_price_unit_cost(vals)
        scraps = super().create(vals_list)
        for scrap in scraps.filtered(
            lambda x: x.state == "done"
            and x.production_id
            and x.production_id.state == "done"
        ):
            scrap.production_id.update_prodution_cost()
        return scraps

    def write(self, vals):
        if "scrap_unit_cost" not in vals:
            vals = self._calculate_price_unit_cost(vals)
        result = super().write(vals)
        for scrap in self.filtered(
            lambda x: x.state == "done"
            and x.production_id
            and x.production_id.state == "done"
        ):
            scrap.production_id.update_prodution_cost()
        return result

    def unlink(self):
        productions = self.env["mrp.production"]
        scraps_with_productions = self.filtered(lambda x: x.production_id)
        if scraps_with_productions:
            productions = scraps_with_productions.mapped("production_id")
        result = super().unlink()
        for production in productions:
            production.update_prodution_cost()
        return result

    def _calculate_price_unit_cost(self, vals):
        if "product_id" in vals:
            product = self.env["product.product"].browse("product_id")
            vals["scrap_unit_cost"] = product.standard_price
        if "lot_id" in vals and vals.get("lot_id", False):
            lot = self.env["stock.lot"].browse("lot_id")
            if lot.purchase_price:
                vals["scrap_unit_cost"] = lot.purchase_price
        if vals.get("scrap_unit_cost") and vals.get("scrap_qty"):
            vals["scrap_cost"] = vals.get("scrap_unit_cost") * vals.get("scrap_qty")
        return vals
