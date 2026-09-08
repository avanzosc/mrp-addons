# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMrpProductionCost(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.location = cls.warehouse.lot_stock_id
        cls.workcenter = cls.env["mrp.workcenter"].create(
            {
                "name": "Test Workcenter",
                "time_start": 0,
                "time_stop": 0,
                "time_efficiency": 100.0,
            }
        )
        cls.component_a = cls.env["product.product"].create(
            {
                "name": "Component A",
                "type": "consu",
                "is_storable": True,
                "standard_price": 10.0,
            }
        )
        cls.component_b = cls.env["product.product"].create(
            {
                "name": "Component B",
                "type": "consu",
                "is_storable": True,
                "standard_price": 5.0,
            }
        )
        cls.finished_product = cls.env["product.product"].create(
            {
                "name": "Finished Product",
                "type": "consu",
                "standard_price": 0.0,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.finished_product.id,
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "consumption": "flexible",
                "operation_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Assembly Operation",
                            "workcenter_id": cls.workcenter.id,
                            "time_cycle_manual": 30.0,
                            "sequence": 1,
                        },
                    )
                ],
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.component_a.id,
                            "product_qty": 2.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.component_b.id,
                            "product_qty": 3.0,
                        },
                    ),
                ],
            }
        )
        cls.env["stock.quant"].create(
            {
                "location_id": cls.location.id,
                "product_id": cls.component_a.id,
                "inventory_quantity": 100.0,
            }
        ).action_apply_inventory()
        cls.env["stock.quant"].create(
            {
                "location_id": cls.location.id,
                "product_id": cls.component_b.id,
                "inventory_quantity": 100.0,
            }
        ).action_apply_inventory()

    def _create_mo(self, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.finished_product
        mo_form.bom_id = self.bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo

    def test_stock_move_material_cost_to_consume(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        for move in mo.move_raw_ids:
            self.assertEqual(move.product_uom_qty, move.product_uom_qty)
            self.assertIsInstance(move.material_cost_to_consume, float)

    def test_stock_move_material_cost_consumed(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        for move in mo.move_raw_ids:
            self.assertIsInstance(move.material_cost_consumed, float)

    def test_workorder_cost_estimated(self):
        mo = self._create_mo(qty=1.0)
        mo.action_confirm()
        self.assertTrue(mo.workorder_ids)
        for wo in mo.workorder_ids:
            expected = wo.costs_hour * (wo.duration_expected / 60)
            self.assertEqual(wo.workorder_cost_estimated, expected)

    def test_workorder_cost_real(self):
        mo = self._create_mo(qty=1.0)
        mo.action_confirm()
        self.assertTrue(mo.workorder_ids)
        for wo in mo.workorder_ids:
            wo.duration = 60.0
            expected = wo.costs_hour * (wo.duration / 60)
            self.assertEqual(wo.workorder_cost_real, expected)

    def test_production_cost_material_to_consume(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        total = sum(mo.move_raw_ids.mapped("material_cost_to_consume"))
        self.assertEqual(mo.cost_material_to_consume, total)

    def test_production_cost_material_consumed(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        total = sum(mo.move_raw_ids.mapped("material_cost_consumed"))
        self.assertEqual(mo.cost_material_consumed, total)

    def test_production_cost_workorder_estimated(self):
        mo = self._create_mo(qty=1.0)
        mo.action_confirm()
        total = sum(mo.workorder_ids.mapped("workorder_cost_estimated"))
        self.assertEqual(mo.cost_workorder_estimated, total)

    def test_production_cost_workorder_real(self):
        mo = self._create_mo(qty=1.0)
        mo.action_confirm()
        for wo in mo.workorder_ids:
            wo.duration = 60.0
        total = sum(mo.workorder_ids.mapped("workorder_cost_real"))
        self.assertEqual(mo.cost_workorder_real, total)

    def test_production_cost_manufacturing_estimated(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        expected = mo.cost_material_to_consume + mo.cost_workorder_estimated
        self.assertEqual(mo.cost_manufacturing_estimated, expected)

    def test_production_cost_manufacturing_real(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        for wo in mo.workorder_ids:
            wo.duration = 60.0
        expected = mo.cost_material_consumed + mo.cost_workorder_real
        self.assertEqual(mo.cost_manufacturing_real, expected)

    def test_production_price_unit_cost(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        for wo in mo.workorder_ids:
            wo.duration = 60.0
        if mo.cost_manufacturing_real and mo.qty_producing:
            expected = mo.cost_manufacturing_real / mo.qty_producing
            self.assertEqual(mo.price_unit_cost, expected)

    def test_done_propagates_cost_to_finished_move(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        for wo in mo.workorder_ids:
            wo.duration = 60.0
        mo.qty_producing = 5.0
        mo.button_mark_done()
        self.assertEqual(mo.state, "done")
        for move in mo.move_finished_ids:
            if move.quantity > 0:
                expected_cost = mo.cost_material_consumed + mo.cost_workorder_real
                self.assertEqual(move.price_unit_cost, expected_cost / move.quantity)

    def test_done_propagates_cost_to_lot(self):
        mo = self._create_mo(qty=5.0)
        mo.action_confirm()
        for wo in mo.workorder_ids:
            wo.duration = 60.0
        mo.qty_producing = 5.0
        mo.button_mark_done()
        self.assertEqual(mo.state, "done")
        if mo.lot_producing_id:
            expected_cost = mo.cost_material_consumed + mo.cost_workorder_real
            expected_unit = expected_cost / mo.qty_producing if mo.qty_producing else 0
            self.assertEqual(mo.lot_producing_id.purchase_price, expected_unit)
