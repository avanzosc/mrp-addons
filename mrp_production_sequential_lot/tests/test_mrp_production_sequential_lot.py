# -*- coding: utf-8 -*-
# Copyright 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.mrp_unitary_production.tests import \
    test_mrp_unitary_production


class TestMrpProductionSequentialLot(
        test_mrp_unitary_production.TestMrpUnitaryProduction):

    def setUp(self):
        super(TestMrpProductionSequentialLot, self).setUp()
        self.production.product_id.track_all = True

    def test_unitary_production_inwizard(self):
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inwizard()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))

    def test_unitary_production_inrouting(self):
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inrouting()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))

    def test_unitary_production_inbom(self):
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inbom()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))

    def test_unitary_production_inorder(self):
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inorder()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))
