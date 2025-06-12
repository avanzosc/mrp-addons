# Copyright 2021 Berezi - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    user_id = fields.Many2one(string="User", comodel_name="res.users")

    @api.onchange("workcenter_id")
    def _onchange_workcenter_id(self):
        if self.workcenter_id and self.workcenter_id.default_user_id:
            self.user_id = self.workcenter_id.default_user_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "workcenter_id" in vals and not vals.get("user_id"):
                workcenter = self.env["mrp.workcenter"].browse(vals["workcenter_id"])
                if workcenter.default_user_id:
                    vals["user_id"] = workcenter.default_user_id.id
        return super().create(vals_list)
