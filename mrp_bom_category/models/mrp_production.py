# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            bom_id = values.get("bom_id")
            if not bom_id:
                continue
            bom = self.env["mrp.bom"].browse(bom_id)
            if bom.exists() and bom.category_id.sequence_id:
                values["name"] = bom.category_id.sequence_id.next_by_id()
        return super().create(vals_list)
