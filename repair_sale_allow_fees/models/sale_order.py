# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_repair_order(self):
        super()._compute_repair_order()
        for rec in self:
            rec.repair_order_ids = (
                rec.mapped("order_line.repair_line_ids.repair_id")
                | rec.mapped("order_line.repair_fee_ids.repair_id")
            ).ids
            rec.repair_order_count = len(rec.repair_order_ids)
