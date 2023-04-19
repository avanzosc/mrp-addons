# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    pallet_id = fields.Many2one(
        string="Pallet",
        comodel_name="product.product")
    packaging_id = fields.Many2one(
        string="Packaging",
        comodel_name="product.product")
