# Copyright 2014 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    mrp_production_follower = fields.Boolean(
        string="Manufacturing orders follower", default=False, copy=False
    )

    def write(self, values):
        result = super().write(values)
        if "mrp_production_follower" in values:
            self._update_productions_followers()
        return result

    def _update_productions_followers(self):
        cond = [("mrp_production_follower", "=", True)]
        users = self.env["res.users"].search(cond)
        if users:
            cond = [("state", "not in", ("done", "cancel", "draft"))]
            productions = self.env["mrp.production"].search(cond)
            if productions:
                productions.write(
                    {
                        "mrp_production_follower_ids": [
                            (6, 0, users.mapped("partner_id").ids)
                        ]
                    }
                )
