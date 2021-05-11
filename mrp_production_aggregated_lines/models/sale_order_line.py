# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields, exceptions, _
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    mrp_production_id = fields.Many2one(
        comodel_name='mrp.production', string='Production',
        copy=False)
    manufacturable_product = fields.Boolean(
        compute="_compute_manufacturable_product")

    @api.depends("product_id", "product_id.route_ids", "product_id.bom_ids",
                 "product_id.bom_ids.type")
    def _compute_manufacturable_product(self):
        manufacture = self.env.ref('mrp.route_warehouse0_manufacture')
        for line in self:
            manufacture_route = (manufacture in line.product_id.route_ids)
            manufacture_bom = any(
                line.product_id.bom_ids.filtered(lambda l: l.type == "normal"))
            line.manufacturable_product = manufacture_route and manufacture_bom

    def _compute_production(self):
        production_obj = self.sudo().env["mrp.production"]
        for line in self:
            line.mrp_production_id = production_obj.with_context(
                active_test=False).search([
                    ("product_id", "=", line.product_id.id),
                    ("sale_line_ids", "=", line.id),
                    ("state", "!=", "cancel"),
                ], limit=1)

    def _action_mrp_dict(self):
        self.ensure_one()
        values = {
            'date_planned_start': self.order_id.date_order,
            'product_id': self.product_id.id or False,
            'product_qty': self.product_uom_qty,
            'product_uom_id': self.product_uom.id,
            'location_dest_id': self.order_id.warehouse_id.lot_stock_id.id,
            'active': False,
            'origin': self.order_id.name,
        }
        return values

    def _get_aggregable_mo_domain(self):
        return [
            ('product_id', '=', self.product_id.id or False),
            ('product_uom_id', '=', self.product_uom.id),
            ('location_dest_id', '=',
             self.order_id.warehouse_id.lot_stock_id.id),
            ('state', '=', 'draft'),
            ('active', '=', False)
        ]
        # week = values.get('date_planned_start').isocalendar()[:2]
        # mo = mos.filtered(
        #     lambda x: week == x.date_planned_start.isocalendar()[:2])

    @api.multi
    def _aggregate_to_mo(self):
        mo_domain = self._get_aggregable_mo_domain()
        mo = self.env['mrp.production'].search(mo_domain, limit=1)
        if mo:
            mo.with_context(sale_line_id=self.id)._update_mo_qty(
                self.product_uom_qty + mo.product_qty)
            add_origin = self.order_id.name
            origin = mo.origin and ", ".join([mo.origin or "", add_origin]) \
                or add_origin
            mo.origin = origin
            self.mrp_production_id = mo.id
        return mo

    @api.multi
    def _action_launch_stock_rule(self):
        for line in self:
            super(SaleOrderLine, line.with_context(
                sale_line_id=line.id,
                active=True,
                production_id=line.mrp_production_id.id)
                  )._action_launch_stock_rule()
        return True

    @api.multi
    def action_create_mrp(self):
        self.ensure_one()
        if self.product_uom_qty <= 0:
            raise exceptions.Warning(_('The quantity must be positive.'))
        aggregated_mo = self._aggregate_to_mo()
        if not aggregated_mo:
            picking_type_id = self.order_id.warehouse_id.manu_type_id.id
            values = self._action_mrp_dict()
            mrp = self.env['mrp.production'].with_context(
                default_picking_type_id=picking_type_id
            ).create(values)
            self.mrp_production_id = mrp.id
            mrp.with_context(sale_line_id=self.id).action_compute()

    @api.multi
    def action_detach_mo(self):
        for line in self:
            production = line.mrp_production_id
            if production.state == 'draft':
                new_qty = production.product_qty - line.product_uom_qty
                if new_qty > 0:
                    production._update_mo_qty(new_qty)
                    production.sale_line_ids = [(3, line.id)]
                    line.mrp_production_id = False
                else:
                    line.mrp_production_id.action_cancel()
                    production.sale_line_ids = [(3, line.id)]
                    line.mrp_production_id = False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_create_mrp_from_lines(self):
        for sale in self:
            for line in sale.order_line.filtered(
                    lambda x: not x.mrp_production_id and
                    x.manufacturable_product):
                try:
                    line.action_create_mrp()
                except exceptions.MissingError:
                    continue

    @api.multi
    def action_confirm(self):
        self.action_create_mrp_from_lines()
        res = super(SaleOrder, self).action_confirm()
        self.mapped('order_line.mrp_production_id').toggle_active()
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for line in self.order_line:
            if line.mrp_production_id.sale_line_ids == line:
                line.mrp_production_id.action_cancel()
            else:
                production = line.mrp_production_id
                if production:
                    production._update_mo_qty(production.product_qty -
                                              line.product_uom_qty)
                    production.sale_line_ids = [(3, line.id)]
        return res


    @api.multi
    def action_show_manufacturing_orders(self):
        self.ensure_one()
        action = self.env.ref("mrp.mrp_production_action")
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(action_dict.get('context', '{}'))
        action_dict['context'].update({
            'active_test': False,
            #'default_sale_order_id': self.id,
        })
        domain = expression.AND([
            [("sale_line_ids", "in", self.order_line.ids)],
        ])
        action_dict.update({
            "domain": domain,
        })
        return action_dict

    @api.multi
    def action_show_scheduled_products(self):
        self.ensure_one()
        action = self.env.ref(
            "mrp_scheduled_products.mrp_production_product_line_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("production_id.sale_line_ids", "in", self.order_line.ids)],
        ])
        action_dict.update({
            "domain": domain,
        })
        return action_dict