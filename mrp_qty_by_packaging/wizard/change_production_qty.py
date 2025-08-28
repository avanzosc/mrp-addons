from odoo import models


class ChangeProductionQty(models.TransientModel):

    _inherit = "change.production.qty"

    def change_prod_qty(self):
        res = super().change_prod_qty()
        for wizard in self:
            production = wizard.mo_id
            if production.product_packaging_id and production.product_qty > 0:
                production.product_packaging_qty = (
                    production.product_qty / production.product_packaging_id.qty
                )
        return res
