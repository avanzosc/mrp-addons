# -*- coding: utf-8 -*-
# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestMrpProductionFixOutMove(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionFixOutMove, self).setUp()
        self.picking_obj = self.env['stock.picking']
        self.procurement_obj = self.env['procurement.order']
        self.production_obj = self.env['mrp.production']
        self.wiz_produce_obj = self.env['mrp.product.produce']
        route_make_to_order_id = self.ref('stock.route_warehouse0_mto')
        route_manufacture_id = self.ref('mrp.route_warehouse0_manufacture')
        self.product_category = self.env['product.category'].create(
            {'name': 'Product category for TestMrpProductionFixOutMove',
             'type': 'normal'})
        self.produce_product = self.env['product.product'].create(
            {'name': 'Product to produce for TestMrpProductionFixOutMove',
             'sale_ok': True,
             'type': 'product',
             'categ_id': self.product_category.id,
             'route_ids': [(6, 0, [route_make_to_order_id,
                                   route_manufacture_id])]})
        self.consume_product = self.env['product.product'].create(
            {'name': 'Product to consume for TestMrpProductionFixOutMove',
             'sale_ok': True,
             'type': 'product',
             'categ_id': self.product_category.id})
        self.mrp_bom = self.env['mrp.bom'].create(
            {'product_tmpl_id': self.produce_product.product_tmpl_id.id,
             'product_qty': 1,
             'bom_line_ids': [(0, 0, {'product_id': self.consume_product.id,
                                      'product_qty': 1})]})
        sale_vals = {
            'name': 'Test mrp production fix out move',
            'partner_id': self.ref('base.res_partner_1'),
            'partner_shipping_id': self.ref('base.res_partner_1'),
            'partner_invoice_id': self.ref('base.res_partner_1'),
            'pricelist_id': self.env.ref('product.list0').id,
            'picking_policy': 'one'}
        sale_line_vals = {
            'product_id': self.produce_product.id,
            'name': self.produce_product.name,
            'product_uom_qty': 200,
            'product_uom': self.produce_product.uom_id.id,
            'price_unit': 25}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.env['sale.order'].create(sale_vals)

    def test_mrp_production_fix_out_move(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_line_id', '=', self.sale_order.order_line[0].id)]
        procurement = self.procurement_obj.search(cond, limit=1)
        cond = [('product_id', '=', procurement.product_id.id),
                ('state', '=', 'confirmed')]
        procurement = self.procurement_obj.search(cond, limit=1)
        if procurement:
            procurement.run()
        production = self.production_obj.search(cond, limit=1)
        production.force_production()
        wiz_vals = {'mode': 'consume_produce',
                    'product_qty': 10,
                    'consume_lines':
                    [(0, 0, {'product_id': self.consume_product.id,
                             'product_qty': 10})]}
        self.wiz = self.wiz_produce_obj.with_context(
            active_model=production._model._name, active_id=production.id,
            active_ids=production.ids).create(wiz_vals)
        self.wiz.with_context(
            active_id=production.id, active_ids=production.ids).do_produce()
        cond = [('group_id', '=', procurement.group_id.id)]
        picking = self.picking_obj.search(cond, limit=1)
        self.assertEqual(
            len(picking.move_lines), 2,
            'Bad number lines in out picking after first produce')
        wiz_vals = {'mode': 'consume_produce',
                    'product_qty': 15,
                    'consume_lines':
                    [(0, 0, {'product_id': self.consume_product.id,
                             'product_qty': 15})]}
        self.wiz2 = self.wiz_produce_obj.with_context(
            active_model=production._model._name, active_id=production.id,
            active_ids=production.ids).create(wiz_vals)
        self.wiz2.with_context(
            active_id=production.id, active_ids=production.ids).do_produce()
        cond = [('group_id', '=', procurement.group_id.id)]
        picking = self.picking_obj.search(cond, limit=1)
        self.assertEqual(
            len(picking.move_lines), 2,
            'Bad number lines in out picking after second produce')
        for line in picking.move_lines:
            self.assertIn(
                line.product_uom_qty, (175.0, 25.0),
                'Bad number lines in out picking after second produce')
