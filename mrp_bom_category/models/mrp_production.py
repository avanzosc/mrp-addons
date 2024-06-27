# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def create(self, values):
        if "bom_id" in values:
            bom = self.env["mrp.bom"].search([("id", "=", values["bom_id"])], limit=1)
            if bom and bom.category_id and bom.category_id.sequence_id:
                values["name"] = bom.category_id.sequence_id.next_by_id()
        production = super(MrpProduction, self).create(values)
        return production
