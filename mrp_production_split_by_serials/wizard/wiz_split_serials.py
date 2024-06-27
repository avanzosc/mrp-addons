# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WizSplitSerials(models.TransientModel):
    _name = "wiz.split.serials"
    _description = "Wizard for split productions"

    mrp_production_ids = fields.Many2many(
        string="MRP Productions",
        comodel_name="mrp.production",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(WizSplitSerials, self).default_get(fields_list)
        if "default_productions" in self.env.context:
            productions = self.env.context.get("default_productions")
            res["mrp_production_ids"] = productions
        return res

    def action_split_productions(self):
        self.ensure_one()
        for production in self.mrp_production_ids:
            production.split_by_serials()
