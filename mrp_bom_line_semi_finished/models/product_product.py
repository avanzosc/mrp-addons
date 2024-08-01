# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    semi_finished = fields.Boolean(
        string="Is semi-finished?",
        related="product_tmpl_id.semi_finished",
        store=True,
        copy=False,
    )
    mrp_bom_ids = fields.One2many(
        string="Mrp BoM", comodel_name="mrp.bom", inverse_name="product_id"
    )
