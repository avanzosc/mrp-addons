# -*- coding: utf-8 -*-
# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.tests.common import TransactionCase


class TestMrpProductionInitialQualityControl(TransactionCase):

    def setUp(self):
        super(TestMrpProductionInitialQualityControl, self).setUp()
        self.production_model = self.env['mrp.production']
        self.inspection_model = self.env['qc.inspection']
        self.qc_trigger_model = self.env['qc.trigger']
        self.product = self.env.ref('product.product_product_4')
        self.test = self.env.ref('quality_control.qc_test_1')
        self.trigger = self.env.ref(
            'mrp_production_initial_quality_control.qc_trigger_mrp_i')
        self.production1 = self.production_model.create({
            'product_id': self.product.id,
            'product_qty': 2.0,
            'product_uom': self.product.uom_id.id})
        inspection_lines = (
            self.inspection_model._prepare_inspection_lines(self.test))
        self.inspection1 = self.inspection_model.create({
            'name': 'TestMrpProductionInitialQualityControl',
            'inspection_lines': inspection_lines})

    def test_mrp_production_initial_quality_control(self):
        self.product.qc_triggers = [
            (0, 0, {'trigger': self.trigger.id,
                    'test': self.test.id, })]
        self.production1.action_confirm()
        self.assertEqual(self.production1.created_inspections, 1,
                         'Only one inspection must be created')
