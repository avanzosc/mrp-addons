# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    stencil_product_ids = fields.One2many(
        string="Stencil products", comodel_name="mrp.bom.stencil.product",
        inverse_name="bom_id", copy=False
    )
