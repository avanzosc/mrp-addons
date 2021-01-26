# Copyright 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


@common.at_install(False)
@common.post_install(True)
class TestRepairFullEditable(common.TransactionCase):

    def setUp(self):
        super(TestRepairFullEditable, self).setUp()
        self.repair = self.env.ref('repair.repair_r1')
        self.product = self.ref('product.product_product_2')
        self.pricelist = self.env.ref('product.list0')

    def test_onchange_product_id(self):
        self.repair.partner_id = ''
        self.repair.product_id = self.product
        self.repair.onchange_product_id()
        self.assertEqual(self.repair.pricelist_id, self.pricelist)
