# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    canal = fields.Boolean(string="Canal", default=False)
    unit_container = fields.Integer(string="Unit/Container")
    palet = fields.Boolean(
        string="Is Palet",
        default=False)
