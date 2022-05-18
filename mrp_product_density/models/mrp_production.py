# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    density = fields.Float(
        string="Density",
        related="product_id.product_tmpl_id.density",
        store=True,
    )