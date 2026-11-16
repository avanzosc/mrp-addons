# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mrp_bom_overhead = fields.Float(
        string="Mrp BoM Overhead",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            mrp_bom_overhead=float(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mrp_bom_overhead", default=15)
            ),
        )
        return res

    def set_values(self):
        result = super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "mrp_bom_overhead", self.mrp_bom_overhead
        )
        return result
