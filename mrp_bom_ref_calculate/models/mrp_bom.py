# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    ref_note = fields.Char(string="Ref. Note")
    code = fields.Char(compute="_compute_code", store=True, copy=False)

    @api.depends(
        "product_tmpl_id",
        "product_tmpl_id.default_code",
        "product_id",
        "product_id.default_code",
        "version",
        "ref_note",
    )
    def _compute_code(self):
        for bom in self:
            default_code = (
                bom.product_id.default_code
                if bom.product_id and bom.product_id.default_code
                else ""
            )
            if (
                not default_code
                and bom.product_tmpl_id
                and bom.product_tmpl_id.default_code
            ):
                default_code = bom.product_tmpl_id.default_code
            code = default_code
            if bom.version:
                code += str(bom.version)
            if bom.ref_note:
                code += str(bom.ref_note)
            bom.code = code
