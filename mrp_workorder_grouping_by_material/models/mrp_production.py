# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    nested_count = fields.Integer(
        string="Nest Count",
        compute="_compute_nested",
    )

    @api.depends(
        "workorder_ids",
        "workorder_ids.nested_line_ids",
        "workorder_ids.nested_line_ids.nest_id",
    )
    def _compute_nested(self):
        for order in self:
            nested = order.mapped("workorder_ids.nested_line_ids.nest_id")
            order.nested_count = len(nested)

    def open_nest(self):
        self.ensure_one()
        nested = self.mapped("workorder_ids.nested_line_ids.nest_id")
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_workorder_grouping_by_material.mrp_workorder_nest_action")
        action["domain"] = expression.AND(
            [[("id", "in", nested.ids)], safe_eval(action.get("domain") or "[]")]
        )
        return action
