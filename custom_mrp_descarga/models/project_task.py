# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    production_id = fields.Many2one(string="Production", comodel_name="mrp.production")
