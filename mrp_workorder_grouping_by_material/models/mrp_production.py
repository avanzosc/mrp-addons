# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools import safe_eval


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    nested_count = fields.Integer(compute="_compute_nested")

    @api.depends("workorder_ids.nested_ids")
    def _compute_nested(self):
        for order in self:
            nested = order.mapped("workorder_ids.nested_ids")
            order.nested_count = len(nested)

    def open_nest(self):
        self.ensure_one()
        nested = self.mapped("workorder_ids.nested_ids")
        action = self.env.ref(
            "mrp_workorder_grouping_by_material.mrp_workorder_nest_action"
        )
        action_dict = action and action.read()[0] or {}
        domain = expression.AND(
            [[("id", "in", nested.ids)], safe_eval(action.domain or "[]")]
        )
        action_dict.update({"domain": domain})
        return action_dict
