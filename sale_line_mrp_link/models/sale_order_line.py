# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    mrp_production_id = fields.Many2one(
        string="MRP Production", comodel_name="mrp.production", copy=False)
