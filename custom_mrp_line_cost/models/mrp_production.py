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
        string="Currency",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id)
    month_id = fields.Many2one(
        string="Month",
        comodel_name="killing.cost",
        compute="_compute_month_id",
        store=True)
    move_to_do_ids = fields.Many2many(
        string="Moves To Do",
        comodel_name="stock.move",
        compute="_compute_move_to_do_ids")
    move_line_to_do_ids = fields.Many2many(
        string="Move Lines To Do",
        comodel_name="stock.move.line",
        compute="_compute_move_line_to_do_ids")
    picking_to_do_ids = fields.Many2many(
        string="Pickings To Do",
        comodel_name="stock.picking",
        compute="_compute_picking_to_do_ids")

    def _compute_move_to_do_ids(self):
        for production in self:
            domain = [("state", "not in", ("done", "cancel")),
                      ("date", ">=", production.date_planned_start),
                      ("picking_code", "=", "outgoing")]
            production.move_to_do_ids = self.env["stock.move"].search(domain)

    def _compute_move_line_to_do_ids(self):
        for production in self:
            domain = [("state", "not in", ("done", "cancel")),
                      ("date", ">=", production.date_planned_start),
                      ("picking_code", "=", "outgoing")]
            production.move_line_to_do_ids = (
                self.env["stock.move.line"].search(domain))

    def _compute_picking_to_do_ids(self):
        for production in self:
            domain = [("state", "not in", ("done", "cancel")),
                      ("scheduled_date", ">=", production.date_planned_start),
                      ("picking_type_code", "=", "outgoing")]
            production.picking_to_do_ids = (
                self.env["stock.picking"].search(domain))

    @api.depends("date_planned_start")
    def _compute_month_id(self):
        for line in self:
            if line.date_planned_start:
                num = line.date_planned_start.month
                month = self.env["killing.cost"].search([("seq", "=", num)], limit=1)
                if month:
                    line.month_id = month.id

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
            if line.move_line_ids:
                canal_lines = line.move_line_ids.filtered(
                    lambda c: c.canal is True)
                if canal_lines and sum(canal_lines.mapped("weight")) != 0:
                    line.canal_cost = sum(
                        canal_lines.mapped("amount"))/sum(
                            canal_lines.mapped("qty_done"))

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

    def action_view_move_to_do(self):
        context = self.env.context.copy()
        return {
            "name": _("Moves To Do"),
            "view_mode": "tree,form",
            "res_model": "stock.move",
            "domain": [("id", "in", self.move_to_do_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }

    def action_view_move_line_to_do(self):
        context = self.env.context.copy()
        return {
            "name": _("Move Lines To Do"),
            "view_mode": "tree,form",
            "res_model": "stock.move.line",
            "domain": [("id", "in", self.move_line_to_do_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }

    def action_view_picking_to_do(self):
        context = self.env.context.copy()
        return {
            "name": _("Pickings To Do"),
            "view_mode": "tree,form",
            "res_model": "stock.picking",
            "domain": [("id", "in", self.picking_to_do_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }
