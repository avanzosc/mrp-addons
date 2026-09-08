# Copyright 2026 Inael
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    olaser_id = fields.Many2one(
        comodel_name="order.olaser", string="Laser Order (Raw Material)"
    )
    lista_olaser_id = fields.Many2one(
        comodel_name="order.olaser", string="Bill of Materials"
    )
    olaser_linea_id = fields.Many2one(
        comodel_name="order.olaser.lista", string="Laser Order Line"
    )
    olaser_retal_control = fields.Boolean(string="Has Scrap Control")
