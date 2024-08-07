# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
##############################################################################
import odoo.tests.common as common


class TestMrpBomComponentChange(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.mrp_bom_model = self.env["mrp.bom"]
        self.mrp_bom_change_model = self.env["mrp.bom.change"]
        vals = {
            "product_tmpl_id": self.env.ref(
                "product.product_product_11_product_template"
            ).id,
            "bom_line_ids": [
                (0, 0, {"product_id": self.env.ref("product.product_product_5").id}),
                (0, 0, {"product_id": self.env.ref("product.product_product_6").id}),
            ],
        }
        self.mrp_bom = self.mrp_bom_model.create(vals)

    def test_mrp_bom_change_without_new_version(self):
        mrp_bom_change = self.mrp_bom_change_model.create(
            {
                "name": "PROBE-1",
                "old_component_id": self.env.ref("product.product_product_5").id,
                "new_component_id": self.env.ref("product.product_product_9").id,
            }
        )
        mrp_bom_change.do_component_change()
        for bom in mrp_bom_change.bom_ids:
            for line in bom.bom_line_ids:
                self.assertNotEqual(
                    self.env.ref("product.product_product_5").id,
                    line.product_id.id,
                    "Incorrect found old component in  MRP BoM",
                )
