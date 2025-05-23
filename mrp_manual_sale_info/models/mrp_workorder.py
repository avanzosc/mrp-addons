# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    manual_sale_id = fields.Many2one(
        comodel_name="sale.order",
        related="production_id.manual_sale_id",
        string="Sale Order",
        readonly=True,
        store=True,
    )
    manual_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="manual_sale_id.partner_id",
        string="Customer",
        readonly=True,
        store=True,
    )
    manual_commitment_date = fields.Datetime(
        related="manual_sale_id.commitment_date",
        string="Commitment Date",
        readonly=True,
        store=True,
    )
    manual_client_order_ref = fields.Char(
        related="manual_sale_id.client_order_ref",
        string="Customer Reference",
        readonly=True,
        store=True,
    )
