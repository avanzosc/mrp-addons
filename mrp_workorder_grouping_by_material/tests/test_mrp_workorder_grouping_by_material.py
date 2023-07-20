# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged

from .common import MrpWorkorderGroupingMaterial


@tagged("post_install", "-at_install")
class TestMrpWorkorderGroupingMaterial(MrpWorkorderGroupingMaterial):
    def test_nest_creation(self):
        test_code = "T3ST"
        workorders = self.env["mrp.workorder"].search([])
        wiz_nest = (
            self.env["nested.new.line"]
            .with_context(active_ids=workorders.ids, active_model="mrp.workorder")
            .create(
                {
                    "nest_code": test_code,
                }
            )
        )
        for line in wiz_nest.line_ids:
            line.qty_producing = line.qty_production
        wiz_nest.action_done()
        nest = self.env["mrp.workorder.nest"].search(
            [
                ("code", "=", test_code),
            ]
        )
        self.assertEqual(nest.state, "draft")
        nest.action_check_ready()
        # self.assertEquals(nest.state, "ready")
        # nest.button_start()
        # self.assertEquals(nest.state, "progress")
        # for line in nest.nested_line_ids.mapped("workorder_id"):
        #     self.assertEquals(line.state, "progress")
        # nest.record_production()
        # self.assertEquals(nest.state, "blocked")
        # nest.nest_unblocked()
        # self.assertEquals(nest.state, "progress")
