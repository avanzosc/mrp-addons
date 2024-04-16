# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    pallet_id = fields.Many2one(
        string="Pallet",
        comodel_name="product.product",
        domain="[('palet', '=', True)]")
    packaging_id = fields.Many2one(
        string="Packaging",
        comodel_name="product.product")

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        if not name:
            return result
        my_name = "%{}%".format(name)
        cond = ["|",
                ("product_tmpl_id", operator, my_name),
                ("code", operator, my_name)]
        boms = self.sudo().search(cond)
        for bom in boms:
            found = False
            for line in result:
                if line and line[0] == bom.id:
                    found = True
                    break
            if not found:
                result.append((bom.id, "{}: {}".format(bom.code, bom.product_tmpl_id.display_name)))
        return result
