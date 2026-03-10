# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class RepairFee(models.Model):
    _inherit = "repair.fee"

    def _get_sale_line_data(self, sale_order):
        self.ensure_one()
        res = {
            "product_id": self.product_id.id,
            "name": self.name,
            "product_uom_qty": self.product_uom_qty,
            "price_unit": self.price_unit,
            "tax_id": self.tax_id and [(6, 0, self.tax_id.ids)] or [],
            "order_id": sale_order.id,
        }
        return res

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line", string="Sale line", copy=False
    )
