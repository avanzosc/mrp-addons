# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    workorder_count = fields.Integer(
        string="# Work Orders", compute="_compute_workorder_count"
    )
    raw_move_line_ids = fields.One2many(
        comodel_name="stock.move.line",
        compute="_compute_raw_lines",
        inverse="_inverse_raw_lines",
        string="Raw Product",
    )
    
    def _compute_workorder_count(self):
        for production in self:
            production.workorder_count = len(production.workorder_ids)

    def _inverse_raw_lines(self):
        """Little hack to make sure that when you change something on these objects,
        it gets saved"""

    @api.depends("move_raw_ids.move_line_ids")
    def _compute_raw_lines(self):
        for production in self:
            production.raw_move_line_ids = production.move_raw_ids.mapped(
                "move_line_ids"
            )

    @api.depends("move_raw_ids", "state", "move_raw_ids.product_uom_qty")
    def _compute_unreserve_visible(self):
        result = super()._compute_unreserve_visible()
        for production in self:
            production.reserve_visible = any(
                [
                    x.state in ("confirmed", "partially_available")
                    for x in production.move_raw_ids
                ]
            )
            production.unreserve_visible = any(
                [x.state == "assigned" for x in production.move_raw_ids]
            )
        return result

    def action_view_workorder(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("mrp.mrp_workorder_todo")
        domain = expression.AND(
            [
                [("id", "in", self.workorder_ids.ids)],
                safe_eval(action.get("domain") or "[]"),
            ]
        )
        context = action.get("context", {}) and ast.literal_eval(action["context"])
        context["default_production_id"] = self.id
        action.update({"domain": domain, "context": context})
        return action
