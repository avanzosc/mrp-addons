# Copyright 2018 Alfredo de la Fuente - Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    origin_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Origin manufacturing order",
    )
    level = fields.Integer(
        string="Level",
        default=0,
    )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def create(self, vals):
        line = super(PurchaseOrderLine, self).create(vals)
        if self.env.context.get("mrp_production_product_line", False):
            line._put_purchase_information_in_scheduled_product()
        return line

    @api.multi
    def write(self, vals):
        result = super(PurchaseOrderLine, self).write(vals)
        if self.env.context.get("mrp_production_product_line", False):
            for line in self:
                line._put_purchase_information_in_scheduled_product()
        return result

    def _put_purchase_information_in_scheduled_product(self):
        self.env.context.get("mrp_production_product_line").write({
            "purchase_order_line_id": self.id,
        })
        if not self.order_id.origin_production_id:
            self.order_id.write({
                "origin_production_id": self.env.context.get("origin_production_id"),
                "level": self.env.context.get("level"),
            })
