# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons.mrp_bom_import.models.mrp_bom_import import convert2str


class MrpBomImport(models.Model):
    _inherit = "mrp.bom.import"

    def _get_line_values(self, row_values):
        values = super(MrpBomImport, self)._get_line_values(row_values)
        if values:
            values.update(
                {
                    "line_position": convert2str(row_values.get("Position", "")),
                }
            )
        return values


class MrpBomLineImport(models.Model):
    _inherit = "mrp.bom.line.import"

    line_position = fields.Char(
        string="Line Position",
    )

    def generate_bom_line_values(self):
        self.ensure_one()
        values = super(MrpBomLineImport, self).generate_bom_line_values()
        values.update(
            {
                "line_position": self.line_position,
            }
        )
        return values
