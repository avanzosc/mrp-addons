# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons.mrp_bom_import.models.mrp_bom_import import check_number


class MrpBomImport(models.Model):
    _inherit = "mrp.bom.import"

    def _get_line_values(self, row_values):
        values = super(MrpBomImport, self)._get_line_values(row_values)
        if values:
            values.update(
                {
                    "long_cut": check_number(row_values.get("long_cut", 0.0)),
                }
            )
        return values


class MrpBomLineImport(models.Model):
    _inherit = "mrp.bom.line.import"

    long_cut = fields.Float(
        string="Long Cut (mm)",
        default=0.0,
    )

    def generate_bom_line_values(self):
        self.ensure_one()
        values = super(MrpBomLineImport, self).generate_bom_line_values()
        values.update(
            {
                "long_cut": self.long_cut,
            }
        )
        return values
