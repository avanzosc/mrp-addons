# Copyright 2025 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductCustomerinfo(models.Model):
    _inherit = "product.customerinfo"

    final_partner_price = fields.Float()
