# Copyright 2020 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestMrpWorkorder(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMrpWorkorder, cls).setUpClass()
        cls.mrp_production_model = cls.env['mrp.production']
        cls.bom_model = cls.env['mrp.bom']
        cls.product_model = cls.env['product.product']
        cls.product_categ_model = cls.env['product.category']
        cls.lot_model = cls.env['stock.production.lot']
        cls.route_model = cls.env['mrp.routing']
        cls.workcenter_model = cls.env['mrp.workcenter']
        cls.operation_model = cls.env['mrp.routing.workcenter']
        unit_id = cls.env.ref('uom.product_uom_unit').id
        cls.product_categ = cls.product_categ_model.create({
            'name': 'Product Category',
            'force_lot_name': True,
        })
        cls.bom_product = cls.product_model.create({
            'name': 'BoM product',
            'uom_id': unit_id,
            'tracking': 'serial',
            'categ_id': cls.product_categ.id,
        })
        cls.lot = cls.lot_model.create({
            'name': 'lot',
            'product_id': cls.bom_product.id
        })
        cls.component1 = cls.product_model.create({
            'name': 'Component1',
            'uom_id': unit_id,
        })
        cls.component2 = cls.product_model.create({
            'name': 'Component2',
            'uom_id': unit_id,
        })
        cls.workcenter = cls.workcenter_model.create({
            'name': 'wc1',
            'resource_calendar_id': cls.env.ref(
                'resource.resource_calendar_std').id,
        })
        cls.route = cls.route_model.create({
            'name': 'route',
            'resource_calendar_id': cls.env.ref(
                'resource.resource_calendar_std').id,
            'operation_ids':
                [(0, 0, {'name': 'op1',
                         'workcenter_id': cls.workcenter.id,
                         })]
        })
        vals = {
            'product_tmpl_id': cls.bom_product.product_tmpl_id.id,
            'product_id': cls.bom_product.id,
            'routing_id': cls.route.id,
            'bom_line_ids':
                [(0, 0, {'product_id': cls.component1.id,
                         'product_qty': 1,
                         'operation_id': cls.route.operation_ids[0].id}),
                 (0, 0, {'product_id': cls.component2.id,
                         'product_qty': 1})],
        }
        cls.mrp_bom = cls.bom_model.create(vals)
        cls.production = cls.mrp_production_model.create({
            'product_id': cls.bom_product.id,
            'product_uom_id': cls.bom_product.uom_id.id,
            'bom_id': cls.mrp_bom.id,
            'routiog_id': cls.route.id,
        })

    def test_force_lot_name(self):
        self.production.button_plan()
        workorder = self.env['mrp.workorder'].search([])[0]
        workorder.button_start()
        workorder.final_lot_id = self.lot.id
        self.assertTrue(workorder.display_force_name)
        self.assertEqual(workorder.final_lot_id.name, 'lot')
        workorder.force_lot_name = 'changed_lot'
        workorder.record_production()
        self.assertEqual(self.lot.name, 'changed_lot')
