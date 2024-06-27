# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    lineal_id = fields.Many2one(
        string="Lineal",
        comodel_name="product.lineal",
        related="product_id.lineal_id",
        store=True,
    )
