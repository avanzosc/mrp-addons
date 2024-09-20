from odoo import models

from odoo.addons.mrp_bom_import.models.mrp_bom_import import convert2str


class MrpBomImport(models.Model):
    _inherit = "mrp.bom.import"

    def _get_line_values(self, row_values):
        res = super()._get_line_values(row_values)
        res.update(
            {
                "layer": convert2str(row_values.get("Layer", "")),
                "designator": convert2str(row_values.get("Designator", "")),
            }
        )
        return res
