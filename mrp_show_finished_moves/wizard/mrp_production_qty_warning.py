# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProductionQtyWarning(models.TransientModel):
    _name = "mrp.production.qty.warning"
    _description = "Quantity Discrepancy Warning"

    production_id = fields.Many2one("mrp.production")
    warning_message = fields.Text(readonly=True)
    yes_label = fields.Char(default="Yes")
    no_label = fields.Char(default="No")

    def action_yes(self):
        self.production_id.update_quantity_done()
        return self.production_id.button_mark_done()

    def action_no(self):
        return {"type": "ir.actions.act_window_close"}
