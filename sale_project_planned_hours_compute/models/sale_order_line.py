
# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _create_project_task(self):
        super(SaleOrderLine, self)._create_project_task()
        if self.order_id.state == 'sale' and self.task_id:
            # Calculate initial planned hours based on sale_hourly_rate
            hours = self.product_uom_qty / self.order_id.project_id.sale_hourly_rate
            self.task_id.planned_hours = hours
