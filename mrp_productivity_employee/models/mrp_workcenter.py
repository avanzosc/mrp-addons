# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    is_external = fields.Boolean(default=False)
