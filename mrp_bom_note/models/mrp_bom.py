# -*- coding: utf-8 -*-
# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    notes = fields.Html(
        string="Notes", copy=False
    )
