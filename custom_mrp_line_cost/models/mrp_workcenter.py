# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    cost_ids = fields.One2many(
        string="Workcenter Costs",
        comodel_name="killing.cost",
        inverse_name="workcenter_id")
