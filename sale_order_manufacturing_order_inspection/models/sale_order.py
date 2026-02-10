# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _put_service_product_in_production(self, production):
        qc_trigger_mrp = self.env["qc.trigger"].get_manufacturing_trigger()
        if not qc_trigger_mrp:
            return
        qc_triggers = (
            production.product_id.qc_triggers
            or production.product_id.product_tmpl_id.qc_triggers
        )
        if not qc_triggers:
            return
        qc_triggers = qc_triggers.filtered(lambda x: x.trigger == qc_trigger_mrp)
        if not qc_triggers:
            return
        service_products = qc_triggers.mapped("service_product_id")
        line = self.order_line.filtered(
            lambda l: l.product_id in service_products
            and l.product_uom_qty == production.product_qty
        )[:1]
        if line:
            production.service_product_id = line.product_id
