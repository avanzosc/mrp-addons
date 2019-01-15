# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestStockProductionLot(common.TransactionCase):

    def setUp(self):
        super(TestStockProductionLot, self).setUp()
        self.produce_obj = self.env['mrp.product.produce']
        cond = [('state', '=', 'draft')]
        self.production = self.env['mrp.production'].search(cond, limit=1)
        self.production.date_planned = '2030-06-01 15:00:00'
        self.production.product_id.write({
            'life_time': 20,
            'use_time': 18,
            'removal_time': 10,
            'alert_time': 7})

    def test_stock_production_lot(self):
        self.production.signal_workflow('button_confirm')
        cond = [('production_id', '=', self.production.id)]
        lot = self.env['stock.production.lot'].search(cond, limit=1)
        self.assertEqual(len(lot), 1, 'Lot not generated')
        self.assertEqual(lot.mrp_date, '2030-06-01', 'Bad mrp date')
        self.assertEqual(lot.life_date, '2030-06-21 00:00:00', 'Bad life date')
        self.assertEqual(lot.use_date, '2030-06-19 00:00:00', 'Bad use date')
        self.assertEqual(
            lot.removal_date, '2030-06-11 00:00:00', 'Bad revoval date')
        self.assertEqual(
            lot.alert_date, '2030-06-08 00:00:00', 'Bad alert date')
        lot.mrp_date = '2030-07-01'
        lot.onchange_mrp_date()
        self.assertEqual(lot.life_date, '2030-07-21 00:00:00', 'Bad life date')
        self.assertEqual(lot.use_date, '2030-07-19 00:00:00', 'Bad use date')
        self.assertEqual(
            lot.removal_date, '2030-07-11 00:00:00', 'Bad revoval date')
        self.assertEqual(
            lot.alert_date, '2030-07-08 00:00:00', 'Bad alert date')
        res = self.produce_obj.with_context(
            active_id=self.production.id).default_get(
            ['lot_id', 'track_production', 'product_id', 'mode', 'product_qty',
             'consume_lines'])
        self.assertEqual(res.get('lot_id', False), lot.id, 'Lot nof found')
        lot.onchange_production_id()
        self.assertEqual(lot.mrp_date, '2030-06-01', 'Bad lot date')
        lot.mrp_date = False
        lot.onchange_mrp_date()
        self.assertFalse(bool(lot.life_date), 'Lot with life date')
        self.assertFalse(bool(lot.use_date), 'Lot with use date')
        self.assertFalse(bool(lot.removal_date), 'Lot with removal date')
        self.assertFalse(bool(lot.alert_date), 'Lot with alert date')
