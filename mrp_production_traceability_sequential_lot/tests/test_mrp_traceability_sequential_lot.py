# -*- coding: utf-8 -*-
# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.mrp_production_sequential_lot.tests import \
    test_mrp_production_sequential_lot


class TestMrpProductionTraceabilitySequentialLot(
        test_mrp_production_sequential_lot.TestMrpProductionSequentialLot):

    def setUp(self):
        super(TestMrpProductionTraceabilitySequentialLot, self).setUp()

    def test_unitary_production_inwizard(self):
        super(TestMrpProductionTraceabilitySequentialLot,
              self).test_unitary_production_inwizard()
        new_wiz = self.wiz.create({})
        self.assertFalse(new_wiz.unitary_production)
        self.assertTrue(new_wiz.lot_id)
        new_wiz.unitary_production = True
        new_wiz._onchange_unitary_production()
        self.assertFalse(new_wiz.lot_id)

    def test_unitary_production_inorder(self):
        super(TestMrpProductionTraceabilitySequentialLot,
              self).test_unitary_production_inorder()
        new_wiz = self.wiz.create({})
        self.assertTrue(new_wiz.unitary_production)
        self.assertFalse(new_wiz.lot_id)

    def test_unitary_production_inrouting(self):
        """Don't repeat this test."""
        pass

    def test_unitary_production_inbom(self):
        """Don't repeat this test."""
        pass

    def test_unitary_production_inwizard_noseq(self):
        """Don't repeat this test."""
        pass

    def test_unitary_production_inrouting_noseq(self):
        """Don't repeat this test."""
        pass

    def test_unitary_production_inbom_noseq(self):
        """Don't repeat this test."""
        pass

    def test_unitary_production_inorder_noseq(self):
        """Don't repeat this test."""
        pass
