from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def onchange_bom_structure(self):
        res = super().onchange_bom_structure()

        if isinstance(res, dict):
            res.pop("warning", None)

        return res
