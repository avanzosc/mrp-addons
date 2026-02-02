# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        result = super().action_confirm()
        for sale in self:
            procurement_groups = self.env["procurement.group"].search(
                [("sale_id", "in", sale.ids)]
            )
            moves = procurement_groups.stock_move_ids
            created_productions = moves.created_production_id
            groups = created_productions.procurement_group_id
            stock_productions = groups.mrp_production_ids
            direct_productions = procurement_groups.mrp_production_ids
            productions = list(stock_productions | direct_productions)
            for production in productions:
                sale._put_service_product_in_production(production)
                production.action_create_inspection_from_of()
        return result

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
