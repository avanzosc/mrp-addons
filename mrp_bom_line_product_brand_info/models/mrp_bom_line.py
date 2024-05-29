# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    manufacturer_codes = fields.Text(
        string="Manufacturer codes", compute="_compute_product_brand_info"
    )
    markings = fields.Text(string="Markings", compute="_compute_product_brand_info")

    def _compute_product_brand_info(self):
        for line in self.filtered(lambda c: c.product_tmpl_id):
            texto = ""
            markings = ""
            for seller in line.product_tmpl_id.seller_ids:
                partner_name = seller.partner_id.name
                code = (
                    ""
                    if not seller.product_brand_id.code
                    else seller.product_brand_id.code
                )
                marking = (
                    ""
                    if not seller.product_brand_id.marking
                    else seller.product_brand_id.marking
                )
                if not texto:
                    texto = "{}: {} - {}".format(partner_name, code, marking)
                else:
                    texto = "{} // {}: {} - {}".format(
                        texto, partner_name, code, marking
                    )
                if not markings:
                    markings = "{}: {}".format(partner_name, marking)
                else:
                    markings = "{} // {}: {}".format(markings, partner_name, marking)
            line.manufacturer_codes = texto
            line.markings = markings

    def get_datas_to_print_bom(self):
        result = super().get_datas_to_print_bom()
        result["manufacturer_codes"] = self.manufacturer_codes
        return result
