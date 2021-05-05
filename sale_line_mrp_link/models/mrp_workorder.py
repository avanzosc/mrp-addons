# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    sale_line_id = fields.Many2one(related='production_id.sale_line_id',
                                   string='Sale order', readonly=True,
                                   store=True)
    partner_id = fields.Many2one(related='production_id.partner_id',
                                 readonly=True, string='Customer', store=True)
    commitment_date = fields.Datetime(
        related='production_id.commitment_date',
        string='Commitment Date', store=True, readonly=True)
