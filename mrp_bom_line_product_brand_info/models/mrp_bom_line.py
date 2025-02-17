from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    markings = fields.Text(compute="_compute_product_brand_info")

    def _compute_product_brand_info(self):
        for line in self.filtered(lambda c: c.product_tmpl_id):
            markings = ""
            for idx, seller in enumerate(
                line.product_tmpl_id.seller_ids.filtered(lambda s: s.product_brand_id)
            ):
                marking = seller.product_brand_id
                brand_code = seller.brand_code

                if brand_code:
                    marking_info = "[{}] {}".format(brand_code, marking.name)
                else:
                    marking_info = "{}".format(marking.name)

                if idx > 0:
                    markings += "\n"

                markings += marking_info

            line.markings = markings

    def get_datas_to_print_bom(self):
        result = super().get_datas_to_print_bom()
        result["markings"] = self.markings
        return result
