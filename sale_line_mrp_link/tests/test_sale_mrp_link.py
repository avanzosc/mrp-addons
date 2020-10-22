# © 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestSaleMrpLink(common.TransactionCase):

    def setUp(self):
        super(TestSaleMrpLink, self).setUp()
        self.sale = self.env.ref('sale.sale_order_6')
        self.product2 = self.env.ref('product.product_product_3')
        self.product = self.env.ref('product.product_product_4')
        self.pricelist = self.env.ref('product.list0')
        self.bom_id = self.env['mrp.bom'].create({
            'product_id': self.product.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
        })

    def test_add_mrp_production(self):
        sale_line = self.sale.order_line[0]
        sale_line.product_id_change()
        sale_line.action_create_mrp()
        self.assertTrue(sale_line.mrp_production_id)
        production = sale_line.mrp_production_id
        self.assertEqual(sale_line, production.sale_line_id)
        self.assertEqual(self.sale, production.sale_order_id)
        self.assertFalse(production.active)
        self.sale.action_confirm()
        self.assertTrue(production.active)

    def test_shortcuts(self):
        res = self.sale.action_show_manufacturing_orders()
        self.assertEqual(res.get('type', False), 'ir.actions.act_window')
