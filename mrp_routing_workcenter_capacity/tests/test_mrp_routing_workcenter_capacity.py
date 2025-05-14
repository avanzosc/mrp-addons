# Copyright 2021 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import tagged

from odoo.addons.mrp.tests import common


@tagged("-at-install", "post-install")
class TestMrpRoutingWorkcenterCapacity(common.TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("mrp.product_product_computer_desk")
        cls.mrp_bom = cls.env.ref("mrp.mrp_bom_desk")
        cls.operation = cls.mrp_bom.operation_ids[:1]
        operation_vals = {
            "capacity": 2,
            "time_cycle_manual": 60,
        }
        cls.operation.write(operation_vals)
        cls.workcenter = cls.operation.workcenter_id
        production_vals = {
            "product_id": cls.product.id,
            "product_uom_id": cls.product.uom_id.id,
            "bom_id": cls.mrp_bom.id,
            "product_qty": 1.0,
        }
        cls.production = cls.env["mrp.production"].create(production_vals)

    def test_mrp_routing_workcenter_capacity(self):
        workorder = self.production.workorder_ids[:1]
        self.assertEqual(workorder.duration_expected, 60.0)
        self.production.product_qty = 2
        self.assertEqual(workorder.duration_expected, 60.0)
        self.production.product_qty = 3
        self.assertEqual(workorder.duration_expected, 120.0)
        operation_vals = {
            "time_start": 10,
            "time_stop": 10,
        }
        self.operation.write(operation_vals)
        self.production._set_qty_producing()
        self.assertEqual(workorder.duration_expected, 140.0)
        workcenter_vals = {
            "default_capacity": 1,
            "time_start": 20,
            "time_stop": 20,
        }
        self.workcenter.write(workcenter_vals)
        result = workorder._get_duration_expected(
            alternative_workcenter=self.workcenter, ratio=1
        )
        self.assertEqual(result, 160.0)
        operation_vals = {
            "time_mode": "auto",
            "time_cycle_manual": 30,
        }
        self.operation.write(operation_vals)
        self.operation._compute_time_cycle()
        self.assertEqual(self.operation.time_cycle, 30.0)
        workorder_vals = {
            "workcenter_id": False,
            "operation_id": False,
        }
        workorder.write(workorder_vals)
        result = workorder._get_duration_expected()
        self.assertEqual(result, 140.0)
