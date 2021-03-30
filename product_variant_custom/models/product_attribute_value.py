# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    is_custom = fields.Boolean(
        'Is custom value',
        help="Allow users to input custom values for this attribute value"
    )
    min_value = fields.Float(string="Min Value", default="-1")
    max_value = fields.Float(string="Max Value", default="-1")
    min_tolerance = fields.Float(string="Min Tolerance")
    max_tolerance = fields.Float(string="Max Tolerance")
