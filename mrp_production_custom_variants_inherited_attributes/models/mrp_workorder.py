# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    product_version_id = fields.Many2one(
        related="production_id.product_version_id")
    custom_value_ids = fields.One2many(
        related="production_id.custom_value_ids")
    product_attribute_ids = fields.One2many(
        related="production_id.product_attribute_ids")
