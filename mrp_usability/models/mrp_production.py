# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import ast

from odoo import api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    move_line_ids = fields.One2many(
        "stock.move.line",
        "production_id",
        string="Move Lines",
        help="Líneas de movimiento asociadas a esta orden de fabricación.",
    )
    move_line_count = fields.Integer(
        string="# Move Lines",
        compute="_compute_move_line_count",
        store=False,
    )
    # Usamos el campo workorder_ids estándar de Odoo y solo añadimos el contador
    workorder_count = fields.Integer(
        string="# Work Orders",
        compute="_compute_workorder_count",
        store=False,
    )

    @api.depends("move_line_ids")
    def _compute_move_line_count(self):
        """Cuenta las líneas de movimiento asociadas."""
        for production in self:
            production.move_line_count = len(production.move_line_ids)

    @api.depends("workorder_ids")
    def _compute_workorder_count(self):
        """Cuenta las órdenes de trabajo asociadas."""
        for production in self:
            production.workorder_count = len(production.workorder_ids)

    def action_view_workorder(self):
        """Abre las órdenes de trabajo desde el botón superior."""
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("mrp.mrp_workorder_todo")
        domain = expression.AND(
            [
                [("id", "in", self.workorder_ids.ids)],
                safe_eval(action.get("domain") or "[]"),
            ]
        )
        context = ast.literal_eval(action.get("context") or "{}")
        context["default_production_id"] = self.id
        action.update({"domain": domain, "context": context})
        return action

    def action_view_move_lines(self):
        """Abre las Move Lines desde el botón superior."""
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_usability.action_mrp_move_lines"
        )
        action["domain"] = [("production_id", "=", self.id)]
        action["context"] = {"default_production_id": self.id}
        return action
