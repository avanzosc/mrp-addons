# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    origin_qty = fields.Float(
        string="Origin Qty")
    dest_qty = fields.Float(
        string="Dest Qty")
    purchase_price = fields.Float(
        string="Purchase Price")
    purchase_unit_price = fields.Float(
        string="Purchase Unit Price")
    price_difference = fields.Float(
        string="Price Difference",
        compute="_compute_price_difference",
        store=True)
    canal_weight = fields.Float(
        string="PMC",
        compute="_compute_canal_weight",
        store=True,
        digits="MRP Standard Price Decimal Precision")
    rto_canal = fields.Float(
        string="Rto. Canal",
        compute="_compute_rto_canal",
        store=True,
        digits="MRP Standard Price Decimal Precision")
    canal_cost = fields.Float(
        string="Canal Cost",
        digits="MRP Standard Price Decimal Precision",
        compute="_compute_canal_cost",
        store=True)
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id.id)

    @api.depends("purchase_price", "move_line_ids", "move_line_ids.qty_done",
                 "move_line_ids.applied_price", "move_line_ids.amount")
    def _compute_price_difference(self):
        for production in self:
            production.price_difference = 0
            if production.purchase_price and production.move_line_ids:
                for line in production.move_line_ids:
                    line.applied_price = line.base_price
                    line.onchange_applied_price()
                dif = production.purchase_price - (
                    sum(production.move_line_ids.mapped("amount")))
                if dif != 0:
                    max_line = max(
                        production.move_line_ids, key=lambda x: x.qty_done)
                    if max_line and max_line.qty_done != 0:
                        max_line.amount = max_line.amount + dif
                        max_line.applied_price = max_line.applied_price + (
                            dif / max_line.qty_done)
                        dif = production.purchase_price - sum(
                            production.move_line_ids.mapped("amount"))
                production.price_difference = dif

    @api.depends("move_line_ids", "move_line_ids.canal",
                 "move_line_ids.qty_done")
    def _compute_canal_weight(self):
        for line in self:
            line.canal_weight = 0
            canal_lines = line.move_line_ids.filtered(
                lambda c: c.canal is True)
            total_weight = sum(line.move_line_ids.mapped("qty_done"))
            canal_weight = sum(canal_lines.mapped("qty_done"))
            if canal_weight != 0:
                line.canal_weight = total_weight / canal_weight

    @api.depends("move_line_ids", "move_line_ids.canal",
                 "move_line_ids.percentage")
    def _compute_rto_canal(self):
        for line in self:
            line.rto_canal = 0
            canal_lines = line.move_line_ids.filtered(
                lambda c: c.canal is True)
            if canal_lines:
                line.rto_canal = sum(canal_lines.mapped("percentage"))

    @api.depends("move_line_ids", "move_line_ids.canal",
                 "move_line_ids.qty_done", "move_line_ids.amount")
    def _compute_canal_cost(self):
        for line in self:
            line.canal_cost = 0
            canal_lines = line.move_line_ids.filtered(
                lambda c: c.canal is True)
            if canal_lines and sum(canal_lines.mapped("weight")) != 0:
                line.canal_cost = sum(
                    canal_lines.mapped("amount"))/sum(
                        canal_lines.mapped("weight"))

    @api.constrains(
        "move_line_ids", "move_line_ids.percentage")
    def _check_lineage_percentage(self):
        for production in self:
            if production.move_line_ids:
                if sum(
                    production.move_line_ids.mapped(
                        "percentage")) > 100:
                    raise ValidationError(
                        _("The sum of the percentages it can't be more than 100."))
