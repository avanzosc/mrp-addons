# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def action_open_wizard(self):
        self.ensure_one()
        return {
            "name": "Work Order",
            "type": "ir.actions.act_window",
            "res_model": "mrp.workorder",
            "res_id": self.id,
            "view_mode": "form",
            "views": [
                (
                    self.env.ref("mrp.mrp_production_workorder_form_view_inherit").id,
                    "form",
                )
            ],
            "target": "current",
        }
