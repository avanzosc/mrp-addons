# Copyright 2018 Alfredo de la Fuente - Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval
from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    origin_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Origin manufacturing order",
        copy=False)
    level = fields.Integer(
        string="Level", default=0, copy=False)
    manufacture_count = fields.Integer(
        string="Manufacturing counting",
        compute='_compute_manufacture_count')
    purchase_count = fields.Integer(
        string="Purchase orders counting",
        compute='_compute_purchase_count')

    @api.multi
    def action_compute(self):
        res = super(MrpProduction, self).action_compute()
        for production in self:
            for line in production.product_line_ids:
                line.onchange_product_id()
        return res

    def _get_manufacturing_orders(self):
        self.ensure_one()
        origin = self.origin_production_id.id or self.id
        cond = [('origin_production_id', '=', origin),
                ('level', '>', self.level)]
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
        action_dict["context"].update({
            "active_test": False,
        })
        domain = expression.AND([
            [("id", "in", productions.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({
            "domain": domain,
        })
        return action_dict

    def _get_purchase_orders(self):
        self.ensure_one()
        purchases = self.mapped("product_line_ids.purchase_order_id")
        child_productions = self._get_manufacturing_orders()
        purchases |= child_productions.mapped(
            "product_line_ids.purchase_order_id")
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
        domain = expression.AND([
            [("id", "in", purchases.ids)],
            safe_eval(action.domain or "[]")])
        action_dict.update({
            "domain": domain,
        })
        return action_dict

    @api.multi
    def button_create_manufacturing_structure(self):
        manufacture = self.env.ref('mrp.route_warehouse0_manufacture', False)
        productions = [self]
        while productions:
            for production in productions:
                if not production.product_line_ids:
                    production.action_compute()
                    for line in production.product_line_ids:
                        line.onchange_product_id()
                lines = production.mapped('product_line_ids').filtered(
                    lambda x: x.route_id.id == manufacture.id and not
                    x.new_production_id and x.make_to_order)
                for line in lines:
                    origin_manufacture_order = (
                        line.production_id.origin_production_id or
                        line.production_id)
                    line.create_automatic_manufacturing_order(
                        origin_manufacture_order,
                        production.analytic_account_id)
                level = production.level
                origin = production.origin_production_id.id or production.id
            level += 1
            cond = [('origin_production_id', '=', origin),
                    ('level', '=', level),
                    ('active', '=', False)]
            productions = self.search(cond)

    def button_create_purchase_order(self):
        buy = self.env.ref(
            'purchase_stock.route_warehouse0_buy', False)
        productions = [self]
        while productions:
            for production in productions:
                if not production.product_line_ids:
                    production.action_compute()
                    for line in production.product_line_ids:
                        line.onchange_product_id()
                lines = production.mapped('product_line_ids').filtered(
                    lambda x: x.route_id.id == buy.id and not
                    x.purchase_order_id and x.make_to_order)
                for line in lines:
                    origin_manufacture_order = (
                        line.production_id.origin_production_id or
                        line.production_id)
                    line.create_automatic_purchase_order(
                        origin_manufacture_order, production.level)
                level = production.level
                origin = production.origin_production_id.id or production.id
            level += 1
            cond = [('origin_production_id', '=', origin),
                    ('level', '=', level),
                    ('active', '=', False)]
            productions = self.search(cond)

    def _get_lines(self, mos):
        if not mos:
            return self.env['mrp.production.product.line']
        lines = mos.mapped('product_line_ids')
        child_mos = lines.filtered(lambda x: x.new_production_id
                                   ).mapped('new_production_id')
        return lines + self._get_lines(child_mos)

    def button_with_child_structure(self):
        lines = self._get_lines(self)
        return {
            "name": _("Scheduled Goods"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "view_type": "form",
            "res_model": "mrp.production.product.line",
            "domain": [("id", "in", lines.ids)]
        }

    @api.multi
    def button_confirm(self):
        return super(MrpProduction, self.with_context(
            procurement_production_id=self.id)).button_confirm()


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    route_id = fields.Many2one(comodel_name="stock.location.route",
                               string="Route")
    make_to_order = fields.Boolean(string="Make to order")
    date = fields.Date(string="Date")
    new_production_id = fields.Many2one(
        comodel_name="mrp.production", string="Manufacturing order")
    production_date_planned_start = fields.Datetime(
        string="Deadline start",
        related="new_production_id.date_planned_start")
    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line", string="Purchase order line")
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order", string="Purchase order",
        related="purchase_order_line_id.order_id", store=True)
    purchase_date_order = fields.Datetime(
        string="Order date", related="purchase_order_id.date_order")
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        related="production_id.analytic_account_id")

    @api.onchange('product_id')
    def onchange_product_id(self):
        make_to_order = self.env.ref(
            'stock.route_warehouse0_mto', False)
        buy = self.env.ref(
            'purchase_stock.route_warehouse0_buy', False)
        manufacture = self.env.ref(
            'mrp.route_warehouse0_manufacture', False)
        self.make_to_order = make_to_order in self.product_id.route_ids
        self.route_id = (
            manufacture if manufacture in self.product_id.route_ids else buy)

    @api.multi
    def button_create_purchase_manufacturing_order(self):
        buy = self.env.ref(
            'purchase_stock.route_warehouse0_buy', False)
        manufacture = self.env.ref(
            'mrp.route_warehouse0_manufacture', False)
        origin_manufacture_order = (
            self.production_id.origin_production_id or self.production_id)
        if self.route_id.id == buy.id:
            self.create_automatic_purchase_order(origin_manufacture_order,
                                                 self.production_id.level)
        if self.route_id.id == manufacture.id:
            self.create_automatic_manufacturing_order(
                origin_manufacture_order,
                self.production_id.analytic_account_id)

    def _get_po_values(self, rule):
        return {
            "company_id": self.production_id.company_id,
            "date_planned": self.production_id.date_planned_start,
            "priority": 1,
            "warehouse_id": (
                self.product_id.warehouse_id or rule.warehouse_id),
        }

    def create_automatic_purchase_order(self, origin_manufacture_order, level):
        if not self.product_id.seller_ids:
            message = _(u"There is no vendor associated to the product {}. "
                        "Please define a vendor for this product.").format(
                self.product_id.name)
            raise ValidationError(message)
        location = (self.product_id.location_id or
                    self.env.ref('stock.stock_location_stock'))
        rule = self.env['procurement.group']._get_rule(
            self.product_id, location, {})
        values = self._get_po_values(rule)
        rule.with_context(
            mrp_production_product_line=self,
            origin_production_id=origin_manufacture_order.id,
            level=self.production_id.level + 1,
            analytic_account_id=self.analytic_account_id)._run_buy(
            self.product_id, self.product_qty, self.product_uom_id, location,
            self.product_id.name, self.production_id.name, values)

    def _get_new_mo_values(self, origin_manufacture_order, analytic_account):
        values = {
            'origin_production_id': origin_manufacture_order.id,
            'level': self.production_id.level + 1,
            'product_qty': self.product_qty,
            'user_id': self.production_id.user_id.id,
        }
        if analytic_account:
            values['analytic_account_id'] = analytic_account.id
        return values

    def create_automatic_manufacturing_order(
            self, origin_manufacture_order,  analytic_account):
        location = (self.product_id.location_id or
                    self.env.ref('stock.stock_location_stock'))
        rule = self.env['procurement.group']._get_rule(
            self.product_id, location, {})
        warehouse = self.env.ref('stock.warehouse0', False)
        values = {'company_id': self.production_id.company_id,
                  'date_planned_start':
                      self.production_id.date_planned_start - relativedelta(
                          days=self.product_id.produce_delay),
                  'date_planned':
                      self.production_id.date_planned_start - relativedelta(
                          days=self.product_id.produce_delay),
                  'warehouse_id': (self.product_id.warehouse_id or
                                   rule.warehouse_id),
                  'picking_type_id': warehouse.manu_type_id,
                  'priority': 1}
        rule.with_context(force_execution=True)._run_manufacture(
            self.product_id, self.product_qty, self.product_uom_id, location,
            self.product_id.name, self.production_id.name, values)
        cond = [('origin', '=', self.production_id.name),
                ('product_id', '=', self.product_id.id),
                ('active', '=', False),
                ('origin_production_id', '=', False)]
        new_production = self.env['mrp.production'].search(cond, limit=1)
        if new_production:
            vals = self._get_new_mo_values(origin_manufacture_order,
                                           analytic_account)
            new_production.write(vals)
            self.new_production_id = new_production
            self.new_production_id.action_compute()
