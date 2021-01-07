# © 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


@common.at_install(False)
@common.post_install(True)
class TestSaleMrpLink(common.TransactionCase):

    def setUp(self):
        super(TestSaleMrpLink, self).setUp()
        manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture')
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        product_obj = self.env["product.product"]
        bom_obj = self.env["mrp.bom"]
        sale_obj = self.env["sale.order"]
        partner = self.env["res.partner"].create({
            "name": "Test Partner",
        })
        self.man_product = product_obj.create({
            "name": "Manufacturing Product",
            "route_ids": [(4, manufacture_route.id), (4, mto_route.id)],
        })
        self.component = product_obj.create({
            "name": "Component",
        })
        self.bom = bom_obj.create({
            "product_tmpl_id": self.man_product.product_tmpl_id.id,
            "type": "normal",
            "bom_line_ids": [(0, 0, {
                "product_id": self.component.id,
                "product_qty": 2.0,
            })],
        })
        self.sale = sale_obj.create({
            "partner_id": partner.id,
            "order_line": [(0, 0, {
                "product_id": self.man_product.id,
            })]
        })

    def test_sale_mrp_link_button(self):
        for line in self.sale.order_line:
            self.assertTrue(line.manufacturable_product)
        self.sale.action_create_mrp_from_lines()
        for line in self.sale.order_line:
            line.invalidate_cache()
            self.assertTrue(line.mrp_production_id)
            self.assertEqual(line, line.mrp_production_id.sale_line_id)
            self.assertEqual(self.sale, line.mrp_production_id.sale_order_id)
            self.assertFalse(line.mrp_production_id.active)
        self.sale.action_confirm()
        for line in self.sale.order_line:
            self.assertTrue(line.mrp_production_id.active)
        self.sale.action_cancel()
        for line in self.sale.order_line:
            self.assertEquals(line.mrp_production_id.state, "cancel")

    def test_sale_mrp_link(self):
        for line in self.sale.order_line:
            self.assertFalse(line.mrp_production_id)
        self.sale.action_confirm()
        for line in self.sale.order_line:
            line.invalidate_cache()
            self.assertTrue(line.mrp_production_id)
            self.assertEqual(line, line.mrp_production_id.sale_line_id)
            self.assertEqual(self.sale, line.mrp_production_id.sale_order_id)
            self.assertTrue(line.mrp_production_id.active)

    def test_phantom_bom(self):
        self.man_product.bom_ids.write({
            "type": "phantom",
        })
        lines = self.env["sale.order.line"].search([
            ("product_id", "=", self.man_product.id)])
        for line in lines:
            self.assertFalse(line.manufacturable_product)

    def test_shortcuts(self):
        manufacturing_button = self.sale.action_show_manufacturing_orders()
        scheduled_button = self.sale.action_show_scheduled_products()
        self.assertIn(
            ("sale_line_id", "in", self.sale.order_line.ids),
            manufacturing_button.get("domain"))
        self.assertIn(
            ("sale_line_id", "in", self.sale.order_line.ids),
            scheduled_button.get("domain"))
