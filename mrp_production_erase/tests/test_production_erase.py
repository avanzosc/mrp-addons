# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProductionErase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProductionErase, cls).setUpClass()
        cls.product_model = cls.env['product.product']
        cls.production_model = cls.env['mrp.production']
        cls.bom_model = cls.env['mrp.bom']
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.bom_product = cls.product_model.create({
            'name': 'BoM product',
            'type': 'product',
            'default_code': 'BMP1',
            'uom_id': cls.uom_unit.id,
            'uom_po_id': cls.uom_unit.id
        })
        cls.component1 = cls.product_model.create({
            'name': 'Component1',
            'type': 'product',
            'default_code': 'cmp1',
            'standard_price': 10.0,
            'uom_id': cls.uom_unit.id,
            'uom_po_id': cls.uom_unit.id,
        })
        cls.component2 = cls.product_model.create({
            'name': 'Component2',
            'type': 'product',
            'default_code': 'cmp2',
            'standard_price': 15.0,
            'uom_id': cls.uom_unit.id,
            'uom_po_id': cls.uom_unit.id,
        })
        vals = {
            'product_tmpl_id': cls.bom_product.product_tmpl_id.id,
            'product_id': cls.bom_product.id,
            'bom_line_ids':
                [(0, 0, {'product_id': cls.component1.id,
                         'product_qty': 2.0}),
                 (0, 0, {'product_id': cls.component2.id,
                         'product_qty': 12.0})],
        }
        cls.mrp_bom = cls.bom_model.create(vals)
        cls.production = cls.production_model.create({
            'product_id': cls.bom_product.id,
            'product_uom_id': cls.bom_product.uom_id.id,
            'bom_id': cls.mrp_bom.id,
        })
        cls.production2 = cls.production_model.create({
            'product_id': cls.bom_product.id,
            'product_uom_id': cls.bom_product.uom_id.id,
            'bom_id': cls.mrp_bom.id,
        })
        cls.wizard = cls.env['mrp.production.erase'].create({})

    def test_erase_productions(self):
        mrp_lst = self.production_model.search(
            [('product_id', '=', self.bom_product.id)])
        self.assertEqual(len(mrp_lst), 2)
        self.production2.state = 'done'
        self.wizard.with_context(
            active_ids=mrp_lst.ids).erase_productions()
        mrp_lst2 = self.production_model.search(
            [('product_id', '=', self.bom_product.id)])
        self.assertEqual(len(mrp_lst2), 1)
