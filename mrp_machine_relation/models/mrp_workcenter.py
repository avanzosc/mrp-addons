# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# Copyright 2015 Daniel Campos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    machine_id = fields.Many2one(
        string="Machine",
        comodel_name="machine",
    )
