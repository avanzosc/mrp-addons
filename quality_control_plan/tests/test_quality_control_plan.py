# -*- coding: utf-8 -*-
# Copyright 2018 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from openerp import fields


class TestQualityControlPlan(common.TransactionCase):

    def setUp(self):
        super(TestQualityControlPlan, self).setUp()
        partner_model = self.env['res.partner']
        product_model = self.env['product.product']
        picking_type_model = self.env['stock.picking.type']
        self.qc_trigger_model = self.env['qc.trigger']
        self.trigger_line_model = self.env['qc.trigger.product_line']
        self.plan_control_model = self.env['product.quality.control.plan.cron']
        self.picking_model = self.env['stock.picking']
        self.lot_model = self.env['stock.production.lot']
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.wizard_model = self.env['stock.transfer_details']
        self.today = date.today()
        self.last_month = self.today - relativedelta(months=1)
        self.next_month = self.today + relativedelta(months=1)
        self.company = self.env.ref('base.main_company')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.company.sample_warehouse_id = self.warehouse
        self.laboratory1 = partner_model.create(
            {'name': 'External Laboratory 1', 'external_laboratory': True})
        self.laboratory2 = partner_model.create(
            {'name': 'External Laboratory 2', 'external_laboratory': True})
        self.supplier = partner_model.create(
            {'name': 'Supplier', 'supplier': True})
        self.plan_product = product_model.create(
            {'name': 'Plan Product', 'type': 'product',
             'subject_to_qcp': True, 'sample_qty': 2})
        self.no_plan_product = product_model.create(
            {'name': 'No Plan Product', 'type': 'product',
             'subject_to_qcp': False})
        self.test = self.env.ref('quality_control.qc_test_1')
        self.test2 = self.test.copy()
        self.test.write(
            {'test_type': 'external',
             'external_laboratory_ids': [(6, 0, [self.laboratory1.id,
                                                 self.laboratory2.id])]})
        self.test2.write(
            {'test_type': 'external',
             'external_laboratory_ids': [(6, 0, [self.laboratory1.id])]})
        self.out_picking_type = picking_type_model.search([
            ('warehouse_id', '=', self.warehouse.id),
            ('code', '=', 'outgoing'),
            ('default_location_dest_id.usage', '=', 'customer')])
        self.trigger = self.qc_trigger_model.search(
            [('picking_type', '=', self.out_picking_type.id)])
        self.trigger_line_model.create(
            {'product': self.plan_product.id, 'trigger': self.trigger.id,
             'test': self.test.id})
        self.trigger_line_model.create(
            {'product': self.plan_product.id, 'trigger': self.trigger.id,
             'test': self.test2.id})
        self.plan_control_model.create(
            {'qc_test_id': self.test.id, 'interval_number': 1,
             'interval_type': 'months', 'next_date': self.last_month,
             'product_id': self.plan_product.id})
        self.plan_control_model.create(
            {'qc_test_id': self.test2.id, 'interval_number': 1,
             'interval_type': 'months', 'next_date': self.next_month,
             'product_id': self.plan_product.id})
        self.lot = self.lot_model.create({
            'product_id': self.plan_product.id, 'name': 'TEST PLAN'})
        value = self.purchase_model.onchange_partner_id(self.supplier.id
                                                        )['value']
        purchase_vals = {
            'partner_id': self.supplier.id,
            'origin': 'TEST QCP',
            'pricelist_id': value.get('pricelist_id'),
            'payment_term_id': value.get('payment_term_id'),
            'fiscal_position': value.get('fiscal_position'),
            'location_id': self.ref('stock.stock_location_locations_partner'),
            'state': 'draft'}
        purchase_line_vals = {
            'product_id': self.plan_product.id,
            'name': 'PLAN PRODUCT',
            'product_qty': 100,
            'price_unit': 5,
            'date_planned': self.today}
        purchase_line_vals2 = {
            'product_id': self.no_plan_product.id,
            'name': 'NORMAL PRODUCT',
            'product_qty': 150,
            'price_unit': 5,
            'date_planned': self.today}
        purchase_vals['order_line'] = [(0, 0, purchase_line_vals),
                                       (0, 0, purchase_line_vals2)]
        self.purchase = self.purchase_model.create(purchase_vals)

    def test_external_test_validation_error(self):
        with self.assertRaises(ValidationError):
            self.test2.write({'external_laboratory_ids': [(6, 0, [])]})
        self.test2.write({
            'test_type': 'internal', 'external_laboratory_ids': [(6, 0, [])]})

    def test_create_sample_purchase_order(self):
        self.purchase.signal_workflow('purchase_confirm')
        sample_no_plan = self.purchase_line_model.search(
            [('order_id.sample_order', '=', True),
             ('order_id.origin_qcp_purchase_id', '=', self.purchase.id),
             ('product_id', '=', self.no_plan_product.id)])
        self.assertFalse(bool(sample_no_plan))
        sample_plan_test1 = self.purchase_line_model.search(
            [('order_id.sample_order', '=', True),
             ('order_id.origin_qcp_purchase_id', '=', self.purchase.id),
             ('product_id', '=', self.plan_product.id),
             ('order_id.qc_test_id', '=', self.test.id)])
        sample_plan_test2 = self.purchase_line_model.search(
            [('order_id.sample_order', '=', True),
             ('order_id.origin_qcp_purchase_id', '=', self.purchase.id),
             ('product_id', '=', self.plan_product.id),
             ('order_id.qc_test_id', '=', self.test2.id)])
        self.assertFalse(bool(sample_plan_test2))
        self.assertTrue(bool(sample_plan_test1))
        self.assertEqual(sample_plan_test1.product_qty,
                         self.plan_product.sample_qty * 2)
        sample_order = sample_plan_test1.order_id
        sample_order.signal_workflow('purchase_confirm')
        laboratory1_pick = self.picking_model.search(
            [('sample_order', '=', sample_order.id),
             ('partner_id', '=', self.laboratory1.id),
             ('picking_type_id', '=', self.out_picking_type.id)])
        self.assertTrue(bool(laboratory1_pick))
        laboratory2_pick = self.picking_model.search(
            [('sample_order', '=', sample_order.id),
             ('partner_id', '=', self.laboratory2.id),
             ('picking_type_id', '=', self.out_picking_type.id)])
        self.assertTrue(bool(laboratory2_pick))
        cron_line = self.plan_product.plan_control_cron_ids.filtered(
            lambda x: x.qc_test_id.id == self.test.id)
        self.assertEqual(cron_line.next_date,
                         fields.Date.to_string(self.today))
        sample_in_picking = sample_plan_test1.move_ids.filtered(
            lambda x: x.picking_id.partner_id.id == sample_order.partner_id.id
            ).mapped('picking_id')
        wiz_id = sample_in_picking.do_enter_transfer_details().get('res_id')
        wizard = self.wizard_model.browse(wiz_id)
        wizard.item_ids.write({'lot_id': self.lot.id})
        wizard.do_detailed_transfer()
        self.assertEqual(laboratory1_pick.state, 'assigned')
        self.assertEqual(laboratory2_pick.state, 'assigned')
        for move in self.purchase.mapped('order_line.move_ids').filtered(
                lambda x: x.product_id.id == self.plan_product.id):
            self.assertEqual(move.restrict_lot_id.id, self.lot.id)
            wiz_id = move.picking_id.do_enter_transfer_details().get('res_id')
            wizard = self.wizard_model.browse(wiz_id)
            for line in wizard.item_ids.filtered(
                    lambda x: x.product_id.id == self.plan_product.id):
                self.assertEqual(line.lot_id.id, self.lot.id)
        wiz_id = laboratory1_pick.do_enter_transfer_details().get('res_id')
        wizard = self.wizard_model.browse(wiz_id)
        wizard.do_detailed_transfer()
        self.assertEqual(laboratory1_pick.created_inspections, 1)
        inspection = laboratory1_pick.qc_inspections
        self.assertEqual(inspection.test.id, sample_order.qc_test_id.id)
