# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mrp_production_historical_ids = fields.One2many(
        string="Historical",
        comodel_name="mrp.production.historical",
        inverse_name="production_id",
        copy=False,
    )
