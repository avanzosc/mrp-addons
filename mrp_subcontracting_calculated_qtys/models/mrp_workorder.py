from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def create_subcontract_purchase(self):
        res = super().create_subcontract_purchase()

        for wo in self:
            if wo.purchase_id and wo.production_id.bom_id:
                bom = wo.production_id.bom_id
                qty_components = sum(
                    line.product_qty
                    for line in bom.bom_line_ids
                    if line.layer in ["TOP", "BOT"]
                )
                new_qty = wo.production_id.product_qty * qty_components
                purchase_line = wo.purchase_id.order_line.filtered(
                    lambda line: line.product_id
                    == wo.service_product_id.product_variant_id
                )
                if purchase_line:
                    purchase_line.product_qty = new_qty

        return res
