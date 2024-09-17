# Copyright 2021 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common
from odoo.exceptions import UserError


@common.at_install(False)
@common.post_install(True)
class MrpSupplierPriceGenerateStructureTest(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(MrpSupplierPriceGenerateStructureTest, cls).setUpClass()
        cls.mrp_production_model = cls.env['mrp.production']
        cls.bom_model = cls.env['mrp.bom']
        cls.product_model = cls.env['product.product']
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier Test',
            'supplier': True,
        })
        cls.supplier2 = cls.env['res.partner'].create({
            'name': 'Supplier Test2',
            'supplier': True,
        })
        cls.supplier3 = cls.env['res.partner'].create({
            'name': 'Supplier Test3',
            'supplier': True,
        })
        bom_product = cls.product_model.create({
            'name': 'BoM product',
        })
        cls.component1 = cls.product_model.create({
            'name': 'Component1',
            'standard_price': 10.0,
        })
        cls.component2 = cls.product_model.create({
            'name': 'Component2',
            'standard_price': 15.0,
            'route_ids': [(4, cls.buy_route.id)],
        })
        cls.env['product.supplierinfo'].create({
            'name': cls.supplier.id,
            'product_tmpl_id': cls.component2.product_tmpl_id.id,
            'min_qty': 1.0,
            'price': 10.0,
        })
        cls.env['product.supplierinfo'].create({
            'name': cls.supplier.id,
            'product_tmpl_id': cls.component2.product_tmpl_id.id,
            'min_qty': 10.0,
            'price': 8.0,
        })
        cls.env['product.supplierinfo'].create({
            'name': cls.supplier2.id,
            'product_tmpl_id': cls.component2.product_tmpl_id.id,
            'min_qty': 10.0,
            'price': 8.0,
        })
        vals = {
            'product_tmpl_id': bom_product.product_tmpl_id.id,
            'product_id': bom_product.id,
            'bom_line_ids':
                [(0, 0, {'product_id': cls.component1.id,
                         'product_qty': 2.0}),
                 (0, 0, {'product_id': cls.component2.id,
                         'product_qty': 12.0}),
                 (0, 0, {'product_id': cls.component2.id,
                         'product_qty': 8.0}),
                 (0, 0, {'product_id': cls.component2.id,
                         'product_qty': 4.0}),
                 ],
        }
        cls.mrp_bom = cls.bom_model.create(vals)
        cls.production = cls.mrp_production_model.create({
            'product_id': bom_product.id,
            'product_uom_id': bom_product.uom_id.id,
            'bom_id': cls.mrp_bom.id,
        })

    def test_mrp_production(self):
        self.production.action_compute()
        count = 0
        for line in self.production.product_line_ids:
            if line.product_id.id == self.component2.id and count==0:
                line.supplier_id = self.supplier2.id
                line.button_create_purchase_manufacturing_order()
                self.assertTrue(
                    line.purchase_order_line_id.order_id.partner_id ==
                    self.supplier2)
                count += 1
            elif line.product_id.id == self.component2.id and count==1:
                line.supplier_id = self.supplier3.id
                line.button_create_purchase_manufacturing_order()
                self.assertTrue(
                    line.purchase_order_line_id.order_id.partner_id ==
                    self.supplier3)
                count += 1
            elif line.product_id.id == self.component2.id:
                line.button_create_purchase_manufacturing_order()
                self.assertTrue(
                    line.purchase_order_line_id.order_id.partner_id ==
                    self.supplier)
        self.assertTrue(self.supplier3 in self.component2.seller_ids.mapped(
            'name'))
