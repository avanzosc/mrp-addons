# -*- coding: utf-8 -*-
# Copyright 2018 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.multi
    @api.depends('sample_order_lst')
    def _compute_sample_order_count(self):
        for record in self:
            record.sample_count = len(record.sample_order_lst)

    sample_order = fields.Boolean(string='Sample Order')
    origin_qcp_purchase_id = fields.Many2one(comodel_name='purchase.order',
                                             string='QC Plan Order')
    qc_test_id = fields.Many2one(comodel_name='qc.test', string='QC Test')
    sample_count = fields.Integer(string='Sample Order Count', store=True,
                                  compute='_compute_sample_order_count')
    sample_order_lst = fields.One2many(comodel_name='purchase.order',
                                       inverse_name='origin_qcp_purchase_id',
                                       string='QC Plan Order')

    @api.multi
    def wkf_approve_order(self):
        res = super(PurchaseOrder, self).wkf_approve_order()
        for record in self:
            if record.needs_creating_sample_orders():
                record.create_sample_orders()
        return res

    @api.multi
    def needs_creating_sample_orders(self):
        self.ensure_one()
        return bool(not self.sample_order)

    @api.multi
    def create_sample_orders(self):
        self.ensure_one()
        for line in self.order_line:
            if line.needs_creating_sample_orders():
                line.create_sample_orders()
        return True

    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id,
                                 group_id):
        new_res = []
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        if not order.sample_order or not res:
            return res
        move_vals = res[0]
        sale_moves = order.get_sale_move_ids(order_line)
        for sale_move in sale_moves:
            new_move_vals = move_vals.copy()
            new_move_vals.update({
                'move_dest_id': sale_move.id,
                'product_uom_qty': order_line.product_id.sample_qty,
                'product_uos_qty': order_line.product_id.sample_qty
            })
            new_res.append(new_move_vals)
        return new_res

    @api.multi
    def get_sale_move_ids(self, order_line):
        self.ensure_one()
        move_ids = []
        for laboratory in self.qc_test_id.external_laboratory_ids:
            move_id = self.create_sale_picking_by_laboratory(order_line,
                                                             laboratory)
            move_ids.append(move_id)
        return move_ids

    @api.multi
    def get_sale_picking_type(self):
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        return self.env['stock.picking.type'].search([
            ('warehouse_id', '=', warehouse.id), ('code', '=', 'outgoing'),
            ('default_location_dest_id.usage', '=', 'customer')], limit=1)

    @api.multi
    def get_sale_picking_vals(self, vals):
        self.ensure_one()
        vals.update({
            'picking_type_id': self.get_sale_picking_type().id,
            'date': self.date_approve,
            'origin': self.name,
            'sample_order': self.id,
        })
        return vals

    @api.multi
    def get_sale_picking_move_vals(self, order_line, vals):
        self.ensure_one()
        picking_type = self.get_sale_picking_type()
        vals.update({
            'name': order_line.name,
            'company_id': self.company_id.id,
            'product_id': order_line.product_id.id,
            'product_uom': order_line.product_id.uom_id.id,
            'product_uom_qty': order_line.product_id.sample_qty,
            'product_uos_qty': order_line.product_id.sample_qty,
            'product_uos':  order_line.product_id.uos_id.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'procure_method': 'make_to_order',
            'purchase_line_id': order_line.id,
            'warehouse_id': picking_type.warehouse_id.id,
            'date_expected': self.date_approve,
            })
        return vals

    @api.multi
    def create_sale_picking_by_laboratory(self, order_line, laboratory):
        self.ensure_one()
        picking_vals = self.get_sale_picking_vals(
            vals={'partner_id': laboratory.id})
        picking_id = self.env['stock.picking'].create(picking_vals)
        picking_vals.update({'picking_id': picking_id.id})
        move_vals = self.get_sale_picking_move_vals(order_line, picking_vals)
        move_id = self.env['stock.move'].create(move_vals)
        picking_id.action_confirm()
        return move_id


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.multi
    def needs_creating_sample_orders(self):
        self.ensure_one()
        return (
            self.product_id.subject_to_qcp and
            self.product_id.plan_control_cron_ids.filtered(
                lambda x: x.next_date <= self.order_id.date_approve))

    @api.multi
    def create_sample_orders(self):
        self.ensure_one()
        for cron_line in self.product_id.plan_control_cron_ids.filtered(
                lambda x: x.next_date <= self.order_id.date_approve):
            self.create_sample_order_by_cron(cron_line)

    @api.multi
    def create_sample_order_by_cron(self, cron_line):
        self.ensure_one()
        purchase_order_vals = self.get_purchase_order_header(cron_line)
        purchase = self.env['purchase.order'].create(purchase_order_vals)
        default_values = {
            'order_id': purchase.id,
            'product_qty': (
                self.product_id.sample_qty * len(cron_line.mapped(
                    'qc_test_id.external_laboratory_ids'))),
            'name': u'[SAMPLE]{}'.format(self.name),
            }
        self.create_sample_line(default=default_values)
        cron_line.sudo().update_next_date()
        return purchase

    @api.multi
    def create_sample_line(self, default={}):
        self.ensure_one()
        return self.copy(default=default)

    @api.multi
    def get_purchase_order_header(self, cron_line):
        self.ensure_one()
        warehouse = self.env['stock.warehouse'].search(
            [('name', 'like', 'Muestra')], limit=1)
        picking_type = self.env['stock.picking.type'].search(
            [('warehouse_id', 'in', warehouse.ids), ('code', '=', 'incoming'),
             ('default_location_src_id.usage', '=', 'supplier')], limit=1)
        partner = self.order_id.partner_id
        onchange_vals = self.order_id.onchange_partner_id(partner.id)['value']
        pricelist = partner.property_product_pricelist_purchase
        vals = {
            'name': self.env['ir.sequence'].get('purchase.order'),
            'origin': self.order_id.name,
            'partner_id': partner.id,
            'location_id': picking_type.default_location_dest_id.id,
            'picking_type_id': picking_type.id,
            'pricelist_id': pricelist.id,
            'currency_id': pricelist.currency_id.id,
            'date_order': self.order_id.date_approve,
            'company_id': self.order_id.company_id.id,
            'fiscal_position': onchange_vals.get('fiscal_position'),
            'payment_term_id': partner.property_supplier_payment_term.id,
            'sample_order': True,
            'origin_qcp_purchase_id': self.order_id.id,
            'qc_test_id': cron_line.qc_test_id.id,
        }
        return vals
