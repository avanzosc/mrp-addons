from odoo import _, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def button_call_wizard_calculate_bom_cost(self):
        self.ensure_one()
        wiz_obj = self.env["wiz.product.product.recalculate.bom.cost2"]
        wiz = wiz_obj.with_context(
            active_id=self.id, active_ids=self.ids, active_model="product.product"
        ).create({})

        return {
            "name": _("Recalculate BoM cost in products"),
            "type": "ir.actions.act_window",
            "res_model": "wiz.product.product.recalculate.bom.cost2",
            "view_type": "form",
            "view_mode": "form",
            "res_id": wiz.id,
            "target": "new",
            "context": {
                "active_id": self.id,
                "active_ids": self.ids,
                "active_model": "product.product",
            },
        }
