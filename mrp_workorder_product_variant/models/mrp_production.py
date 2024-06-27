# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.onchange("bom_id", "product_id")
    def _onchange_workorder_ids(self):
        result = super(MrpProduction, self)._onchange_workorder_ids()
        if self.bom_id and self.workorder_ids:
            for workorder in self.workorder_ids:
                attributes = self.product_id.product_template_attribute_value_ids
                op = workorder.operation_id
                if (
                    op
                    and op.bom_product_template_attribute_value_ids
                    and (
                        not any(
                            [
                                line in attributes
                                for line in op.bom_product_template_attribute_value_ids
                            ]
                        )
                    )
                ):
                    self.workorder_ids = [(3, workorder.id)]
            for line in self.move_raw_ids:
                routing = []
                for workorder in self.workorder_ids:
                    if workorder.operation_id not in routing:
                        routing.append(workorder.operation_id)
                if (
                    line.bom_line_id
                    and line.bom_line_id.operation_id
                    and line.bom_line_id.operation_id not in routing
                ):
                    self.move_raw_ids = [(3, line.id)]
        return result
