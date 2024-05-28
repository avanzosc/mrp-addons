# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError


class MrpProductionProductLine(models.Model):
    _inherit = "mrp.production.product.line"

    @api.multi
    def create_automatic_purchase_order(self, origin_manufacture_order, level):
        if not self.product_id.seller_ids:
            message = _(
                "There is no vendor associated to the product {}. "
                "Please define a vendor for this product."
            ).format(self.product_id.name)
            raise ValidationError(message)
        location = self.production_id.location_src_id or self.env.ref(
            "stock.stock_location_stock"
        )
        rule = self.env["procurement.group"]._get_rule(self.product_id, location, {})
        if not rule:
            raise UserError(
                _(
                    'No procurement rule found in location "%s" for product "%s".\n '
                    "Check routes configuration."
                )
                % (location.display_name, self.product_id.display_name)
            )
        values = self._get_po_values(rule)
        rule.with_context(
            mrp_production_product_line=self,
            origin_production_id=origin_manufacture_order.id,
            level=self.production_id.level + 1,
            analytic_account_id=self.analytic_account_id,
        ).create_merge_purchase_line(
            self.product_id,
            self.product_qty,
            self.product_uom_id,
            location,
            self.product_id.name,
            self.production_id.name,
            False,
            values,
        )
