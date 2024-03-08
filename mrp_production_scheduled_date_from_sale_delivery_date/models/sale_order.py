# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if "commitment_date" in vals:
            for sale in self:
                if sale.mrp_production_ids:
                    sale.mrp_production_ids.write(
                        {"date_planned_start": vals.get("commitment_date")})
        return result
