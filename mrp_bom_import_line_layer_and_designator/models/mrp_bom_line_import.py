from odoo import fields, models


class MrpBomLineImport(models.Model):
    _inherit = "mrp.bom.line.import"

    layer = fields.Char(
        comodel_name="mrp.bom.line",
        related="bom_line_id.layer",
    )
    designator = fields.Char(
        comodel_name="mrp.bom.line",
        related="bom_line_id.designator",
    )
