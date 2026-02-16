# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.tools import float_is_zero, float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    product_packaging_id = fields.Many2one(
        string="Packaging",
        comodel_name="product.packaging",
        domain="[('sales', '=', True), ('product_id','=',product_id)]",
        check_company=True,
        copy=True,
    )
    product_packaging_qty = fields.Float(string="Packaging Quantity", copy=False)

    packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        string="Product Packaging",
        domain="[('product_id','=',product_id)]",
    )

    @api.onchange("product_packaging_id")
    def _onchange_product_packaging_id(self):
        if (
            self.product_packaging_id
            and self.product_qty > 0
            and self.product_packaging_id.qty > 0
        ):
            self.product_packaging_qty = (
                self.product_qty / self.product_packaging_id.qty
            )
        else:
            self.product_packaging_qty = 0
            self.product_qty = 1

    @api.onchange("product_packaging_qty")
    def _onchange_product_packaging_qty(self):
        if self.product_packaging_id and self.product_packaging_qty:
            self.product_qty = (
                self.product_packaging_qty * self.product_packaging_id.qty
            )

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        if self.product_packaging_id and self.product_uom_qty:
            packaging_uom = self.product_packaging_id.product_uom_id
            packaging_uom_qty = self.product_uom_id._compute_quantity(
                self.product_qty, packaging_uom
            )
            self.product_packaging_qty = float_round(
                packaging_uom_qty / self.product_packaging_id.qty,
                precision_rounding=packaging_uom.rounding,
            )

    def write(self, vals):
        res = super().write(vals)
        for production in self:
            if (
                "product_packaging_qty" in vals
                and production.state == "confirmed"
                and production.product_packaging_id
            ):
                expected_qty = (
                    production.product_packaging_qty
                    * production.product_packaging_id.qty
                )
                if not float_is_zero(
                    expected_qty - production.product_qty,
                    precision_rounding=production.product_uom_id.rounding,
                ):
                    wizard = self.env["change.production.qty"].create(
                        {
                            "mo_id": production.id,
                            "product_qty": expected_qty,
                        }
                    )
                    wizard.change_prod_qty()
        return res
