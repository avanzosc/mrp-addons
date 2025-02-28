from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    markings = fields.Text(compute="_compute_product_brand_info")

    def _compute_product_brand_info(self):
        for line in self.filtered(lambda c: c.product_tmpl_id):
            markings = set()
            for seller in line.product_tmpl_id.seller_ids.filtered(
                lambda s: s.product_brand_id
            ):
                brand_code = seller.brand_code
                marking_name = seller.product_brand_id.name

                if brand_code:
                    marking_info = "[{}] {}".format(brand_code, marking_name)
                else:
                    marking_info = "{}".format(marking_name)

                markings.add(marking_info)

            line.markings = "\n".join(markings)

    def get_datas_to_print_bom(self):
        result = super().get_datas_to_print_bom()
        result["markings"] = self.markings
        return result
