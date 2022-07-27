# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    container = fields.Integer(string="Containers")
    unit = fields.Integer(string="Unit")
    product_unit_container = fields.Integer(
        string="Product Unit/Container",
        related="product_id.unit_container",
        store=True)
    unit_container = fields.Integer(
        string="Unit/Container")
    weight = fields.Float(
        string="Weight",
        compute="_compute_weight",
        store=True,
        digits="MRP Standard Price Decimal Precision")
    percentage = fields.Float(
        string="%",
        compute="_compute_percentage",
        store=True,
        digits="MRP Standard Price Decimal Precision")
    base_price = fields.Float(
        digits="MRP Standard Price Decimal Precision",
        compute="_compute_base_price",
        store=True)
    applied_price = fields.Float(
        string="Applied Price",
        digits="MRP Standard Price Decimal Precision")
    expense_kg = fields.Boolean(
        string="Cost/Kgm",
        related="move_id.bom_line_id.expense_kg",
        store=True)
    canal = fields.Boolean(
        string="Canal",
        related="product_id.canal",
        store=True)

    @api.depends("move_id", "move_id.bom_line_id",
                 "move_id.bom_line_id.coefficient", "move_id.bom_line_id.cost",
                 "move_id.bom_line_id.expense_kg", "production_id",
                 "production_id.purchase_unit_price",
                 "production_id.month_id", "production_id.month_id.cost")
    def _compute_base_price(self):
        for line in self:
            if line.production_id:
                cost = line.move_id.bom_line_id.coefficient * (
                    line.production_id.purchase_unit_price)
                if (
                    line.production_id) and not (
                        line.production_id.date_planned_start):
                    raise ValidationError(
                        _("You must introduce the planned date.")
                        )
                if line.move_id.bom_line_id.cost:
                    cost = line.move_id.bom_line_id.cost
                if line.expense_kg is True:
                    cost += line.production_id.month_id.cost
                line.base_price = cost
                line.onchange_base_price()

    @api.depends("unit", "qty_done")
    def _compute_weight(self):
        for line in self:
            if line.unit != 0:
                line.weight = line.qty_done / line.unit

    @api.depends("qty_done", "production_id", "production_id.origin_qty")
    def _compute_percentage(self):
        for line in self:
            if line.production_id.origin_qty != 0:
                line.percentage = (
                    line.qty_done * 100 / line.production_id.origin_qty)

    @api.onchange("container")
    def onchange_container(self):
        if self.container:
            self.unit = self.product_unit_container * self.container
            self.unit_container = self.product_unit_container

    @api.onchange("unit")
    def onchange_unit(self):
        if self.unit and self.container != 0:
            self.unit_container = self.unit / self.container

    @api.onchange("qty_done")
    def onchange_base_price(self):
        self.ensure_one()
        if self.base_price:
            self.applied_price = self.base_price
        self.onchange_applied_price()

    @api.onchange("qty_done", "applied_price")
    def onchange_applied_price(self):
        if self.qty_done and self.applied_price:
                self.amount = self.applied_price * self.qty_done
