# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

from odoo.addons.mrp_scheduled_products.tests.common import MrpProductionCommon


@common.at_install(False)
@common.post_install(True)
class TestMrpProductionGenerateStructure(MrpProductionCommon):
    def test_child_structure(self):
        self.production.button_with_child_structure()

    def test_create_manufacture_structure(self):
        self.assertFalse(self.production.product_line_ids)
        self.production.action_compute()
        self.assertTrue(self.production.product_line_ids)
        self.assertFalse(self.production.manufacture_count)
        self.production.button_create_manufacturing_structure()
        self.production.invalidate_cache()
        self.assertEqual(
            len(self.production._get_manufacturing_orders()),
            self.production.manufacture_count,
        )
        self.assertEqual(
            len(
                self.production.product_line_ids.filtered(
                    lambda ln: ln.route_id == self.manufacture_route
                    and not ln.make_to_order
                )
            ),
            self.production.manufacture_count,
        )

    def test_create_purchase_structure(self):
        self.assertFalse(self.production.product_line_ids)
        self.production.action_compute()
        self.assertTrue(self.production.product_line_ids)
        self.assertFalse(self.production.purchase_count)
        self.production.button_create_purchase_order()
        self.production.invalidate_cache()
        self.assertEqual(
            len(self.production._get_purchase_orders()), self.production.purchase_count
        )
        self.assertEqual(
            len(
                self.production.product_line_ids.filtered(
                    lambda ln: ln.route_id == self.buy_route and not ln.make_to_order
                )
            ),
            self.production.purchase_count,
        )

    def test_confirm_manufacture(self):
        self.assertFalse(self.production.product_line_ids)
        self.production.action_compute()
        self.assertTrue(self.production.product_line_ids)
        self.assertEqual(self.production.state, "draft")
        self.production.button_confirm()
        self.assertEqual(self.production.state, "confirmed")
