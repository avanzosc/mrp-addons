# Copyright 2018 Alfredo de la Fuente - Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    origin_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Origin manufacturing order",
        copy=False,
    )
    level = fields.Integer(
        string="Level",
        default=0,
        copy=False,
    )
    manufacture_count = fields.Integer(
        string="Manufacturing counting",
        compute="_compute_manufacture_count",
    )
    purchase_count = fields.Integer(
        string="Purchase orders counting",
        compute="_compute_purchase_count",
    )

    def _get_manufacturing_orders(self):
        self.ensure_one()
        origin = self.origin_production_id.id or self.id
        cond = [("origin_production_id", "=", origin), ("level", ">", self.level)]
        productions = self.with_context(active_test=False).search(cond)
        return productions

    @api.multi
    def _compute_manufacture_count(self):
        for production in self:
            productions = production._get_manufacturing_orders()
            production.manufacture_count = len(productions)

    @api.multi
    def button_show_manufacturing_orders(self):
        self.ensure_one()
        productions = self._get_manufacturing_orders()
        action = self.env.ref("mrp.mrp_production_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(action_dict.get("context", "{}"))
        action_dict["context"].update(
            {
                "active_test": False,
            }
        )
        domain = expression.AND(
            [[("id", "in", productions.ids)], safe_eval(action.domain or "[]")]
        )
        action_dict.update(
            {
                "domain": domain,
            }
        )
        return action_dict

    def _get_purchase_orders(self):
        self.ensure_one()
        purchases = self.mapped("product_line_ids.purchase_order_id")
        child_productions = self._get_manufacturing_orders()
        purchases |= child_productions.mapped("product_line_ids.purchase_order_id")
        return purchases

    @api.multi
    def _compute_purchase_count(self):
        for production in self:
            purchases = production._get_purchase_orders()
            production.purchase_count = len(purchases)

    @api.multi
    def button_show_purchase_orders(self):
        self.ensure_one()
        purchases = self._get_purchase_orders()
        action = self.env.ref("purchase.purchase_rfq")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND(
            [[("id", "in", purchases.ids)], safe_eval(action.domain or "[]")]
        )
        action_dict.update(
            {
                "domain": domain,
            }
        )
        return action_dict

    @api.multi
    def button_create_manufacturing_structure(self):
        manufacture = self.env.ref("mrp.route_warehouse0_manufacture", False)
        productions = [self]
        while productions:
            for production in productions:
                if not production.product_line_ids:
                    production.action_compute()
                    for line in production.product_line_ids:
                        line.onchange_product_id()
                lines = production.mapped("product_line_ids").filtered(
                    lambda x: x.route_id.id == manufacture.id
                    and not x.new_production_id
                    and not x.make_to_order
                )
                for line in lines:
                    origin_manufacture_order = (
                        line.production_id.origin_production_id or line.production_id
                    )
                    line.create_automatic_manufacturing_order(
                        origin_manufacture_order, production.analytic_account_id
                    )
                level = production.level
                origin = production.origin_production_id.id or production.id
            level += 1
            cond = [
                ("origin_production_id", "=", origin),
                ("level", "=", level),
                ("active", "=", False),
            ]
            productions = self.search(cond)

    def button_create_purchase_order(self):
        buy = self.env.ref("purchase_stock.route_warehouse0_buy", False)
        productions = [self]
        while productions:
            for production in productions:
                if not production.product_line_ids:
                    production.action_compute()
                    for line in production.product_line_ids:
                        line.onchange_product_id()
                lines = production.mapped("product_line_ids").filtered(
                    lambda x: x.route_id.id == buy.id
                    and not x.purchase_order_id
                    and not x.make_to_order
                )
                for line in lines:
                    origin_manufacture_order = (
                        line.production_id.origin_production_id or line.production_id
                    )
                    line.create_automatic_purchase_order(
                        origin_manufacture_order, production.level
                    )
                level = production.level
                origin = production.origin_production_id.id or production.id
            level += 1
            cond = [
                ("origin_production_id", "=", origin),
                ("level", "=", level),
                ("active", "=", False),
            ]
            productions = self.search(cond)

    def _get_lines(self, mos):
        if not mos:
            return self.env["mrp.production.product.line"]
        lines = mos.mapped("product_line_ids")
        child_mos = lines.filtered(lambda x: x.new_production_id).mapped(
            "new_production_id"
        )
        return lines + self._get_lines(child_mos)

    def button_with_child_structure(self):
        lines = self._get_lines(self)
        return {
            "name": _("Scheduled Goods"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "view_type": "form",
            "res_model": "mrp.production.product.line",
            "domain": [("id", "in", lines.ids)],
            "context": {"hide_production_id": False},
        }

    @api.multi
    def button_confirm(self):
        return super(
            MrpProduction, self.with_context(procurement_production_id=self.id)
        ).button_confirm()
