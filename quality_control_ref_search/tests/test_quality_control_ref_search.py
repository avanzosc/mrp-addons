# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import odoo.tests.common as common


class TestQualityControlRefSearch(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.product = cls.env["product.product"].create({"name": "Test product"})

    def test_quality_control_ref_search(self):
        inspection_vals = {
            "object_id": "%s,%d" % (self.product._name, self.product.id),
        }
        self.inspection = self.inspection_model.create(inspection_vals)
        self.assertNotEqual(
            self.inspection.ref_model_name, False, "Inspections without reference model"
        )
        self.assertNotEqual(
            self.inspection.ref_name, False, "Inspections without reference name"
        )
