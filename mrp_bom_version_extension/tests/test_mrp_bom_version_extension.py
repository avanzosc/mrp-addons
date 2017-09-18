# -*- coding: utf-8 -*-
# Copyright 2017 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestMrpBomVersionExtension(common.TransactionCase):

    def setUp(self):
        super(TestMrpBomVersionExtension, self).setUp()
        self.parameter_model = self.env['ir.config_parameter']
        self.bom_model = self.env['mrp.bom']
        self.company = self.env.ref('base.main_company')
        vals = {
            'company_id': self.company.id,
            'product_tmpl_id':
                self.env.ref('product.product_product_11_product_template').id,
            'bom_line_ids':
                [(0, 0, {'product_id':
                         self.env.ref('product.product_product_5').id}),
                 (0, 0, {'product_id':
                         self.env.ref('product.product_product_6').id})],
        }
        self.mrp_bom = self.bom_model.create(vals)

    def test_mrp_bom_versioning(self):
        wiz_config_obj = self.env['mrp.config.settings']
        record = wiz_config_obj.new()
        record.bom_historicize = False
        record.set_parameter_bom_historicize()
        self.mrp_bom.button_activate()
        self.mrp_bom.button_new_version()
        self.assertTrue(self.mrp_bom.active)
        self.assertNotEqual(self.mrp_bom.state, 'historical')
        record.bom_historicize = True
        record.set_parameter_bom_historicize()
        self.mrp_bom.button_activate()
        self.mrp_bom.button_new_version()
        self.assertFalse(self.mrp_bom.active)
        self.assertEqual(self.mrp_bom.state, 'historical')

    def test_param_config(self):
        wiz_config_obj = self.env['mrp.config.settings']
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', 'bom.historicize')])
        self.assertEqual(rec.value, 'True')
        rec.unlink()
        record = wiz_config_obj.new()
        record.set_parameter_bom_historicize()
        data = record.get_default_parameter_bom_historicize()
        self.assertFalse(data['bom_historicize'])
        record.bom_historicize = True
        record.set_parameter_bom_historicize()
        data = record.get_default_parameter_bom_historicize()
        self.assertTrue(data['bom_historicize'])
