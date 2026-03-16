# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    repair_fee_ids = fields.One2many(
        comodel_name="repair.fee",
        inverse_name="sale_line_id",
        string="Repair Fees",
        required=False,
    )
