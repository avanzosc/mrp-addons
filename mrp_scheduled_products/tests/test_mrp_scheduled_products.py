# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase
from odoo.exceptions import MissingError


class MrpScheduledProducts(SavepointCase):

    def setUp(cls):
        super(MrpScheduledProducts, cls).setUp()
        cls.mrp_production_model = cls.env['mrp.production']
        cls.bom_model = cls.env['mrp.bom']
        cls.product_model = cls.env['product.product']
        unit_id = cls.ref('uom.product_uom_unit')
        dozen_id = cls.ref('uom.product_uom_dozen')
        bom_product = cls.product_model.create({
            'name': 'BoM product',
            'uom_id': unit_id,
        })
        cls.component1 = cls.product_model.create({
            'name': 'Component1',
            'standard_price': 10.0,
            'uom_id': dozen_id,
            'uom_po_id': unit_id,
        })
        cls.component2 = cls.product_model.create({
            'name': 'Component2',
            'standard_price': 15.0,
            'uom_id': unit_id,
            'uom_po_id': unit_id,
        })
        vals = {
            'product_tmpl_id': bom_product.product_tmpl_id.id,
            'product_id': bom_product.id,
            'bom_line_ids':
                [(0, 0, {'product_id': cls.component1.id,
                         'product_qty': 2.0}),
                 (0, 0, {'product_id': cls.component2.id,
                         'product_qty': 12.0})],
        }
        cls.mrp_bom = cls.bom_model.create(vals)
        cls.production = cls.mrp_production_model.create({
            'product_id': bom_product.id,
            'product_uom_id': bom_product.uom_id.id,
        })

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
            'product_id': self.component1.id,
        })
        with self.assertRaises(MissingError):
            self.production.action_compute()

    def test_scheduled_good_onchange(self):
        line = self.env['mrp.production.product.line'].new({
            'product_id': self.component1,
        })
        self.assertFalse(line.product_uom_id)
        line._onchange_product_id()
        self.assertEquals(line.product_uom_id, line.product_id.uom_id)
