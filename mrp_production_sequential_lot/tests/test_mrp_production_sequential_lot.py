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
        self.ir_sequence_model = self.env['ir.sequence']
        self.lot_sequence = self.browse_ref(
            'mrp_production_sequential_lot.lot_sequence')

    def test_unitary_production_inwizard(self):
        code = self._get_next_code()
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inwizard()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name, code)

    def test_unitary_production_inrouting(self):
        code = self._get_next_code()
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inrouting()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name, code)

    def test_unitary_production_inbom(self):
        code = self._get_next_code()
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inbom()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name, code)

    def test_unitary_production_inorder(self):
        code = self._get_next_code()
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inorder()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name, code)

    def test_unitary_production_inwizard_noseq(self):
        self.lot_sequence.active = False
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inwizard()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))

    def test_unitary_production_inrouting_noseq(self):
        self.lot_sequence.active = False
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inrouting()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))

    def test_unitary_production_inbom_noseq(self):
        self.lot_sequence.active = False
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inbom()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))

    def test_unitary_production_inorder_noseq(self):
        self.lot_sequence.active = False
        super(TestMrpProductionSequentialLot,
              self).test_unitary_production_inorder()
        self.assertTrue(self.production.mapped(
            'move_created_ids2.restrict_lot_id'))
        self.assertEqual(self.production.mapped(
            'move_created_ids2.restrict_lot_id')[:1].name,
            u"{}-1".format(self.production.name))

    def _get_next_code(self):
        d = self.ir_sequence_model._interpolation_dict()
        prefix = self.ir_sequence_model._interpolate(
            self.lot_sequence.prefix, d)
        suffix = self.ir_sequence_model._interpolate(
            self.lot_sequence.suffix, d)
        code = (prefix + ('%%0%sd' % self.lot_sequence.padding %
                          self.lot_sequence.number_next_actual) + suffix)
        return code
