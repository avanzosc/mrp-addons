# -*- coding: utf-8 -*-
# Copyright 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestMrpUnitaryProduction(common.TransactionCase):

    def setUp(self):
        super(TestMrpUnitaryProduction, self).setUp()
        production_model = self.env['mrp.production']
        product_model = self.env['product.product']
        unit_uom = self.browse_ref('product.product_uom_unit')
        self.unit_kg = self.browse_ref('product.product_uom_kgm')
        product = product_model.create({
            'name': 'Production Product',
            'uom_id': unit_uom.id,
        })
        self.product1 = product_model.create({
            'name': 'Consume Product',
            'uom_id': unit_uom.id,
        })
        self.routing = self.env['mrp.routing'].create({
            'name': 'Routing'
        })
        self.bom = self.env['mrp.bom'].create({
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_id': product.id,
            'bom_line_ids': [(0, 0, {
                'product_id': self.product1.id,
                'product_qty': 1.0,
                'product_uom': self.product1.uom_id.id,
            })],
            'routing_id': self.routing.id,
        })
        self.production = production_model.create({
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_qty': 2.0,
            'bom_id': self.bom.id,
            'routing_id': self.routing.id,
        })
        self.production.action_compute()
        self.production.action_confirm()
        self.wiz = self.env['mrp.product.produce'].with_context(
            active_model=self.production._model._name,
            active_id=self.production.id,
            active_ids=self.production.ids)

    def test_unitary_production_inwizard(self):
        self.assertFalse(self.production.unitary_production)
        new_wiz = self.wiz.create({})
        self.assertFalse(new_wiz.unitary_production)
        new_wiz.unitary_production = True
        new_wiz._onchange_unitary_production()
        new_wiz.do_produce()
        self.assertEqual(len(self.production.move_created_ids2), 1)
        self.assertNotEqual(sum(self.production.mapped(
            'move_created_ids2.product_uom_qty')), self.production.product_qty)

    def test_unitary_production_inrouting(self):
        self.routing.unitary_production = True
        self.assertFalse(self.bom.unitary_production)
        self.assertFalse(self.production.unitary_production)
        new_wiz = self.wiz.create({})
        self.assertTrue(new_wiz.unitary_production)
        new_wiz._onchange_unitary_production()
        new_wiz.do_produce()
        self.assertNotEqual(sum(self.production.mapped(
            'move_created_ids2.product_uom_qty')), self.production.product_qty)

    def test_unitary_production_inbom(self):
        self.bom.unitary_production = True
        self.assertFalse(self.routing.unitary_production)
        self.assertFalse(self.production.unitary_production)
        new_wiz = self.wiz.create({})
        self.assertTrue(new_wiz.unitary_production)
        new_wiz._onchange_unitary_production()
        new_wiz.do_produce()
        self.assertNotEqual(sum(self.production.mapped(
            'move_created_ids2.product_uom_qty')), self.production.product_qty)

    def test_unitary_production_inorder(self):
        self.production.unitary_production = True
        self.assertFalse(self.bom.unitary_production)
        self.assertFalse(self.routing.unitary_production)
        new_wiz = self.wiz.create({})
        self.assertTrue(new_wiz.unitary_production)
        new_wiz._onchange_unitary_production()
        new_wiz.do_produce()
        self.assertNotEqual(sum(self.production.mapped(
            'move_created_ids2.product_uom_qty')), self.production.product_qty)
