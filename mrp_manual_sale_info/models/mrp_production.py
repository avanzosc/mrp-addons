# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    manual_sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
    )
    manual_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
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

    @api.constrains("manual_sale_id", "manual_partner_id")
    def _check_auto_renew_canceled_lines(self):
        for rec in self:
            if (
                rec.manual_sale_id
                and rec.manual_sale_id.partner_id != rec.manual_partner_id
            ):
                raise ValidationError(
                    _("Customer must be same as customer from Sale Order!")
                )

    @api.onchange("manual_sale_id")
    def _onchange_manual_sale_id(self):
        if self.manual_sale_id:
            self.manual_partner_id = self.manual_sale_id.partner_id
