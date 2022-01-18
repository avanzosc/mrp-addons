# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from .common import MrpProductionCommon
from odoo.tests import common
from odoo.exceptions import MissingError


@common.at_install(False)
@common.post_install(True)
class TestMrpScheduledProducts(MrpProductionCommon):

    def test_mrp_production(self):
        self.production.action_compute()
        self.assertEqual(len(self.production.bom_id.bom_line_ids),
                         len(self.production.product_line_ids))
        self.assertEqual(len(self.mrp_bom.bom_line_ids),
                         len(self.production.product_line_ids))
        self.assertFalse(self.production.move_raw_ids)
        self.assertFalse(self.production.finished_move_line_ids)
        self.production.button_confirm()

    def test_mrp_production_error(self):
        self.production.write({
            "product_id": self.buy_component.id,
        })
        with self.assertRaises(MissingError):
            self.production.action_compute()

    def test_scheduled_line_onchange(self):
        line = self.env["mrp.production.product.line"].new({
            "product_id": self.buy_component.id,
        })
        self.assertFalse(line.product_uom_id)
        line._onchange_product_id()
        self.assertEquals(line.product_uom_id, line.product_id.uom_id)
