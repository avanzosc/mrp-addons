# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    show_button_bom_line = fields.Boolean(
        string="Show button BoM Components",
        compute="_compute_show_button_bom_line")
    mrp_bom_line_semi_finished_ids = fields.Many2many(
        string="MRP BoM Components with semi finished product",
        comodel_name="mrp.bom.line",
        compute="_compute_show_button_bom_line")

    def _compute_show_button_bom_line(self):
        for line in self:
            show_button_bom_line = False
            my_bom_lines = self.env["mrp.bom.line"]
            if line.product_id and line.product_id.mrp_bom_ids:
                for bom in line.product_id.mrp_bom_ids:
                    bom_lines = bom.bom_line_ids.filtered(
                        lambda x: x.semi_finished)
                    for bom_line in bom_lines:
                        show_button_bom_line = True
                        my_bom_lines += bom_line
            line.show_button_bom_line = show_button_bom_line
            if my_bom_lines:
                line.mrp_bom_line_semi_finished_ids = [
                    (6, 0, my_bom_lines.ids)]

    def action_show_bom_lines_semi_finished(self):
        self.ensure_one()
        action = self.env.ref(
            "mrp_bom_line_semi_finished.mrp_bom_line_tree_action")
        action_dict = action and action.read()[0]
        action_dict["context"] = safe_eval(
            action_dict.get("context", "{}"))
        domain = expression.AND([
            [("id", "in", self.mrp_bom_line_semi_finished_ids.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({"domain": domain})
        return action_dict
