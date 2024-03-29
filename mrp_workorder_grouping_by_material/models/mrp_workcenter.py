# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    nesting_required = fields.Boolean(string="Nesting Required")
    copy_production_qty = fields.Boolean(string="Copy Nest Quantity")
