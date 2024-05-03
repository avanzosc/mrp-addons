# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stencil_category = fields.Boolean(
        string="Stencil category",
        related="categ_id.stencil_category",
        store=True,
        copy=False,
    )
