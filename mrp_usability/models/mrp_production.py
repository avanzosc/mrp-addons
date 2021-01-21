# Copyright 2019 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from odoo.addons import decimal_precision as dp


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    moves_to_consume_count = fields.Integer(
        string='# Consume Moves',
        compute='_compute_moves_to_consume_count')
    qty_remaining = fields.Float(
        string="Quantity To Be Produced",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_qty_remaining")

    @api.depends('move_raw_ids', 'move_raw_ids.scrapped')
    def _compute_moves_to_consume_count(self):
        for production in self.filtered(
                lambda c: c.move_raw_ids):
            moves = production.mapped('move_raw_ids').filtered(
                lambda x: not x.scrapped)
            production.moves_to_consume_count = len(moves) if moves else 0

    @api.depends("product_qty", "qty_produced")
    def _compute_qty_remaining(self):
        for production in self:
            production.qty_remaining = (
                production.product_qty - production.qty_produced)
