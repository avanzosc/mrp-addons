# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    extended_quality_control_ids = fields.One2many(
        string="Production control",
        comodel_name="extended.quality.control",
        inverse_name="mrp_production_id",
    )

    def action_confirm(self):
        test_obj = self.env["qc.test"]
        line_obj = self.env["qc.trigger.product_line"]
        lines = self.env["qc.trigger.product_line"]
        qc_trigger = self.env.ref(
            "mrp_production_initial_quality_control.qc_trigger_mrp_i"
        )
        cond = [("test_for_manufacturing_orders", "=", True)]
        tests = test_obj.search(cond)
        if tests:
            for production in self:
                for test in tests:
                    if not test.product_ids or (
                        test.product_ids
                        and production.product_id.id in test.product_ids.ids
                    ):
                        vals = {
                            "trigger": qc_trigger.id,
                            "test": test.id,
                            "user": self.env.user.id,
                            "product": production.product_id.id,
                        }
                        lines += line_obj.create(vals)
        result = super().action_confirm()
        if lines:
            lines.unlink()
        return result
