# © 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestSaleMrpLink(common.TransactionCase):

    def setUp(self):
        super(TestSaleMrpLink, self).setUp()
        self.sale = self.env.ref('sale.sale_order_6')
        self.sale2 = self.env.ref('sale.sale_order_7')
        self.product = self.env.ref('product.product_product_4')
        self.product2 = self.env.ref('product.product_product_25')
        self.pricelist = self.env.ref('product.list0')
        self.bom_id = self.env['mrp.bom'].create({
            'product_id': self.product.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'bom_line_ids': [(0, 0, {
                'product_id': self.product2.id,
                'product_qty': 2,
            })]
        })
        self.bom_id2 = self.env['mrp.bom'].create({
            'product_id': self.product2.id,
            'product_tmpl_id': self.product2.product_tmpl_id.id,
        })
        self.mo_route_id = self.env.ref('mrp.route_warehouse0_manufacture')
        self.product.route_ids = [(6, 0, [self.mo_route_id.id])]

    def test_add_mrp_production(self):
        sale_line = self.sale.order_line[0]
        sale_line.product_id_change()
        self.sale.action_create_mrp_from_lines()
        self.assertTrue(sale_line.mrp_production_id)
        production = sale_line.mrp_production_id
        self.assertEqual(sale_line, production.sale_line_id)
        self.assertEqual(self.sale, production.sale_order_id)
        self.assertFalse(production.active)
        self.sale.action_confirm()
        self.sale2.action_confirm()
        self.assertTrue(production.active)
        product_lines_len = production.action_compute()
        self.assertTrue(product_lines_len, 1)

    def test_shortcuts(self):
        res = self.sale.action_show_manufacturing_orders()
        res2 = self.sale.action_show_scheduled_products()
        self.assertEqual(res.get('type', False), 'ir.actions.act_window')
        self.assertEqual(res2.get('type', False), 'ir.actions.act_window')
