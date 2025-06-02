# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    production_control_ids = fields.One2many(
        "mrp.production.control", "workorder_id", string="Production Control Lines"
    )
