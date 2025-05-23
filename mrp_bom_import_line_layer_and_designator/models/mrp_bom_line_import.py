from odoo import fields, models


class MrpBomLineImport(models.Model):
    _inherit = "mrp.bom.line.import"

    layer = fields.Char()
    designator = fields.Char()

    def generate_bom_line_values(self):
        self.ensure_one()
        bom_line = super().generate_bom_line_values()
        bom_line.update(
            {
                "layer": self.layer,
                "designator": self.designator,
            }
        )
        return bom_line
