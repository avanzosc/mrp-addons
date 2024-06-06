# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
##############################################################################
import odoo.tests.common as common


class TestMrpBomVersionComponentChange(common.TransactionCase):

    def setUp(self):
        super(TestMrpBomVersionComponentChange, self).setUp()
        self.mrp_bom_model = self.env["mrp.bom"]
        self.mrp_bom_change_model = self.env["mrp.bom.change"]
        vals = {"product_tmpl_id":
                self.env.ref("product.product_product_11_product_template").id,
                "active": True,
                "bom_line_ids":
                [(0, 0, {"product_id":
                         self.env.ref("product.product_product_5").id}),
                 (0, 0, {"product_id":
                         self.env.ref("product.product_product_6").id})],
                }
        self.mrp_bom_without_new_version = self.mrp_bom_model.create(vals)
        vals = {"product_tmpl_id":
                self.env.ref("product.product_product_4_product_template").id,
                "active": True,
                "bom_line_ids":
                [(0, 0, {"product_id":
                         self.env.ref("product.product_product_7").id}),
                 (0, 0, {"product_id":
                         self.env.ref("product.product_product_8").id})],
                }
        self.mrp_bom_with_new_version = self.mrp_bom_model.create(vals)

    def test_mrp_bom_version_change_without_new_version(self):
        mrp_bom_change = self.mrp_bom_change_model.create(
            {"name": "PROBE-1",
             "create_new_version": False,
             "old_component_id": self.env.ref("product.product_product_5").id,
             "new_component_id": self.env.ref("product.product_product_9").id,
             })
        mrp_bom_change.do_component_change()
        for bom in mrp_bom_change.bom_ids:
            self.assertEqual(
                bom.version, 1,
                "Incorrect version for MRP BoM without new version")
            for line in bom.bom_line_ids:
                self.assertNotEqual(
                    self.env.ref("product.product_product_5").id,
                    line.product_id.id,
                    "Incorrect found old component in  MRP BoM without new"
                    " version")

    def test_mrp_bom_version_change_with_new_version(self):
        mrp_bom_change = self.mrp_bom_change_model.create(
            {"name": "PROBE-2",
             "create_new_version": True,
             "old_component_id": self.env.ref("product.product_product_7").id,
             "new_component_id": self.env.ref("product.product_product_9").id,
             })
        mrp_bom_change.do_component_change()
        for bom in mrp_bom_change.bom_ids:
            self.assertEqual(bom.version, 2,
                             "Incorrect version for MRP BoM with new version")
            for line in bom.bom_line_ids:
                self.assertNotEqual(
                    self.env.ref("product.product_product_7").id,
                    line.product_id.id,
                    "Incorrect found old component in  MRP BoM with new"
                    " version")
