# Copyright 2022 Gonzalo Nuin - AvanzOSC
# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    category_id = fields.Many2one(
        comodel_name="mrp.bom.category",
        string="Category",
    )
    alt_category_id = fields.Many2one(
        comodel_name="mrp.bom.category",
        string="Alternate Category",
    )
