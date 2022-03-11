# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_operation_line(self, bom, qty, level):
        result = super()._get_operation_line(bom, qty, level)
        if not bom.operation_ids:
            return result
        operations = []
        total = 0.0
        qty = bom.product_uom_id._compute_quantity(qty, bom.product_tmpl_id.uom_id)
        for operation in bom.operation_ids:
            operation_cycle = float_round(
                qty / operation.capacity, precision_rounding=1, rounding_method="UP")
            duration_expected = (
                operation_cycle * (operation.time_cycle + (
                    operation.time_stop + operation.time_start)))
            total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            operations.append({
                "level": level or 0,
                "operation": operation,
                "name": operation.name + " - " + operation.workcenter_id.name,
                "duration_expected": duration_expected,
                "total": self.env.company.currency_id.round(total),
            })
        return operations
