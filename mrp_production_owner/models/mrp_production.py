# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    owner_id = fields.Many2one(
        string="Owner",
        comodel_name="res.partner",
        check_company=True,
        copy=False,
    )

    def button_mark_done(self):
        result = super().button_mark_done()
        for production in self.filtered(lambda x: x.state == "done" and x.owner_id):
            for move in production.move_finished_ids:
                move.move_line_ids.write({"owner_id": production.owner_id.id})
        return result

    def write(self, vals):
        result = super().write(vals)
        if "owner_id" in vals:
            for production in self.filtered(lambda x: x.state == "done"):
                owner = vals.get("owner_id", False)
                for move in production.move_finished_ids:
                    move.move_line_ids.write({"owner_id": owner})
        return result
