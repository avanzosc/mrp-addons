# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    coefficient = fields.Float(
        string='Coefficient',
        digits="Coef Decimal Precision")
    expense_kg = fields.Boolean(string='Production Cost', default=False)
    cost = fields.Float(
        string='Fixed Cost',
        digits="Coef Decimal Precision")
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id.id)

    @api.onchange("product_id")
    def onchange_cost(self):
        if self.product_id:
            self.cost = self.product_id.standard_price
