# Copyright 2018 Alfredo de la Fuente - Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    origin_production_id = fields.Many2one(comodel_name="mrp.production",
                                           string="Origin manufacturing order")
    level = fields.Integer(string='Level', default=0)
    manufacture_count = fields.Integer(
        string="Manufacturing counting", compute='_compute_manufacture_count')
    purchase_count = fields.Integer(
        string="Purchase orders counting", compute='_compute_purchase_count')

    @api.multi
    def action_compute(self):
        res = super(MrpProduction, self).action_compute()
        for production in self:
            for line in production.product_lines:
                line.onchange_product_id()
        return res

    @api.multi
    def _compute_manufacture_count(self):
        for production in self:
            origin = production.origin_production_id.id or production.id
            cond = [('origin_production_id', '=', origin),
                    ('level', '>', production.level),
                    '|', ('active', '=', True), ('active', '=', False)]
            productions = self.search(cond)
            production.manufacture_count = len(productions)

    @api.multi
    def button_show_manufacturing_orders(self):
        self.ensure_one()
        origin = self.origin_production_id.id or self.id
        cond = [('origin_production_id', '=', origin),
                ('level', '>', self.level),
                '|', ('active', '=', True), ('active', '=', False)]
        productions = self.search(cond)
        return {'name': _('Productions'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,kanban,form,calendar,pivot,graph',
                'view_type': 'form',
                'res_model': 'mrp.production',
                'domain': [('id', 'in', productions.ids),
                           '|', ('active', '=', True), ('active', '=', False)]}

    @api.multi
    def _compute_purchase_count(self):
        for production in self:
            origin = production.origin_production_id.id or production.id
            cond = [('origin_production_id', '=', origin)]
            purchases = self.env['purchase.order'].search(cond)
            production.purchase_count = len(purchases)

    @api.multi
    def button_show_purchase_orders(self):
        self.ensure_one()
        origin = self.origin_production_id.id or self.id
        cond = [('origin_production_id', '=', origin)]
        purchases = self.env['purchase.order'].search(cond)
        return {'name': _('Purchase orders'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,kanban,form,pivot,graph,calendar',
                'view_type': 'form',
                'res_model': 'purchase.order',
                'domain': [('id', 'in', purchases.ids)]}

    @api.multi
    def button_create_manufacturing_structure(self):
        manufacture = self.env.ref('mrp.route_warehouse0_manufacture', False)
        productions = [self]
        while productions:
            for production in productions:
                if not production.product_lines:
                    production.action_compute()
                    for line in production.product_lines:
                        line.onchange_product_id()
                lines = production.mapped('product_lines').filtered(
                    lambda x: x.route_id.id == manufacture.id and not
                    x.new_production_id and x.make_to_order)
                for line in lines:
                    origin_manufacture_order = (
                        line.production_id.origin_production_id or
                        line.production_id)
                    line.create_automatic_manufacturing_order(
                        origin_manufacture_order)
                level = production.level
                origin = production.origin_production_id.id or production.id
            level += 1
            cond = [('origin_production_id', '=', origin),
                    ('level', '=', level),
                    ('active', '=', False)]
            productions = self.search(cond)

    def button_create_purchase_order(self):
        buy = self.env.ref(
            'purchase.route_warehouse0_buy', False)
        productions = [self]
        while productions:
            for production in productions:
                if not production.product_lines:
                    production.action_compute()
                    for line in production.product_lines:
                        line.onchange_product_id()
                lines = production.mapped('product_lines').filtered(
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

    @api.onchange('product_id')
    def onchange_product_id(self):
        make_to_order = self.env.ref(
            'stock.route_warehouse0_mto', False)
        buy = self.env.ref(
            'purchase.route_warehouse0_buy', False)
        manufacture = self.env.ref(
            'mrp.route_warehouse0_manufacture', False)
        self.make_to_order = False
        if make_to_order and self.product_id and make_to_order.id\
                in self.product_id.route_ids.ids:
            self.make_to_order = True
            if buy and buy.id in self.product_id.route_ids.ids:
                self.route_id = buy.id
            if manufacture and manufacture.id in self.product_id.route_ids.ids:
                self.route_id = manufacture.id

    @api.multi
    def button_create_purchase_manufacturing_order(self):
        buy = self.env.ref(
            'purchase.route_warehouse0_buy', False)
        manufacture = self.env.ref(
            'mrp.route_warehouse0_manufacture', False)
        origin_manufacture_order = (
            self.production_id.origin_production_id or self.production_id)
        if self.route_id.id == buy.id:
            self.create_automatic_purchase_order(origin_manufacture_order,
                                                 self.production_id.level)
        if self.route_id.id == manufacture.id:
            self.create_automatic_manufacturing_order(origin_manufacture_order)

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
        values = {'company_id': self.production_id.company_id,
                  'date_planned': fields.Datetime.now(),
                  'priority': 1,
                  'warehouse_id': (self.product_id.warehouse_id or
                                   rule.warehouse_id)}
        rule.with_context(
            mrp_production_product_line=self,
            origin_production_id=origin_manufacture_order.id,
            level=self.production_id.level + 1)._run_buy(
            self.product_id, self.product_qty, self.product_uom_id, location,
            self.product_id.name, self.production_id.name, values)

    def create_automatic_manufacturing_order(self, origin_manufacture_order):
        location = (self.product_id.location_id or
                    self.env.ref('stock.stock_location_stock'))
        rule = self.env['procurement.group']._get_rule(
            self.product_id, location, {})
        warehouse = self.env.ref('stock.warehouse0', False)
        values = {'company_id': self.production_id.company_id,
                  'date_planned': fields.Datetime.now(),
                  'warehouse_id': (self.product_id.warehouse_id or
                                   rule.warehouse_id),
                  'picking_type_id': warehouse.manu_type_id,
                  'priority': 1}
        rule._run_manufacture(
            self.product_id, self.product_qty, self.product_uom_id, location,
            self.product_id.name, self.production_id.name, values)
        cond = [('origin', '=', self.production_id.name),
                ('product_id', '=', self.product_id.id),
                ('active', '=', False),
                ('origin_production_id', '=', False)]
        new_production = self.env['mrp.production'].search(cond, limit=1)
        if new_production:
            new_production.write(
                {'origin_production_id': origin_manufacture_order.id,
                 'level': self.production_id.level + 1})
            self.new_production_id = new_production
            self.new_production_id.onchange_product_id()
            self.new_production_id.action_compute()
