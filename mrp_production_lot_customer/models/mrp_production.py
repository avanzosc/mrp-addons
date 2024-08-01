# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    lot_customer_id = fields.Many2one(
        string="Customer of lot",
        comodel_name="res.partner",
        related="lot_producing_id.customer_id",
        store=True,
        copy=False,
    )
