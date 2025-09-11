# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_control_ids = fields.One2many(
        "mrp.production.control",
        "manufacturing_order_id",
        string="Production Control Lines",
    )

    production_min_controlled = fields.Integer(
        string="Controlled Pieces",
        compute="_compute_production_min_controlled",
        store=True,
    )

    @api.depends(
        "production_control_ids.workorder_id",
        "production_control_ids.controlled_pieces",
    )
    def _compute_production_min_controlled(self):
        for production in self:
            workorder_sums = {}
            for line in production.production_control_ids:
                wo = line.workorder_id
                if wo:
                    workorder_sums.setdefault(wo.id, 0)
                    workorder_sums[wo.id] += line.controlled_pieces or 0
            production.production_min_controlled = (
                min(workorder_sums.values()) if workorder_sums else 0
            )
