# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        res = super().action_confirm()
        lines = self.env["mrp.bom.line"].search(
            [
                ("component_template_id", "!=", False),
                ("product_id", "!=", False),
            ]
        )
        lines.sudo().write({"product_id": False})
        return res
