# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from .common import MrpWorkorderGroupingMaterial
from odoo.tests import common, tagged
from odoo import fields


@tagged("post_install", "-at_install")
class TestMrpWorkorderGroupingMaterial(MrpWorkorderGroupingMaterial):

    def test_nest_creation(self):
        self.production_id.onchange_product_id()
        self.production_id._onchange_bom_id()
        self.production_id._onchange_move_raw()
        self.production_id.action_confirm()
        self.production_id.button_plan()
        workorders = self.env["mrp.workorder"].search([])
        wiz_nest = self.env["nested.new.line"].with_context(
            active_ids=workorders.ids, active_model="mrp.workorder").create({})
        wiz_nest.onchange_product_id()
        wiz_nest.action_done()
        nest = self.env["mrp.workorder.nest"].search([])
        nest.nest_start()
        self.assertEquals(nest.state, "ready")
        nest.button_start()
        self.assertEquals(nest.state, "progress")
        for line in nest.nested_line_ids.mapped("workorder_id"):
            self.assertEquals(line.state, "progress")
        nest.record_production()
        self.assertEquals(nest.state, "blocked")
        nest.nest_unblocked()
        self.assertEquals(nest.state, "progress")
