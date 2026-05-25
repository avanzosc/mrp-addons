# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

KILLING_COST_DIGITS = (16, 3)
MRP_PRICE_DIGITS = (16, 5)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _default_pallet_id(self):
        if "default_production_id" in self.env.context:
            result = (
                self.env["mrp.production"]
                .browse(self.env.context.get("default_production_id"))
                .pallet_id.id
            )
        else:
            result = False
        return result

    def _default_container(self):
        result = 0
        if "default_production_id" in self.env.context:
            result = 1
        return result

    container = fields.Integer(string="Containers", default=_default_container)
    unit = fields.Integer()
    product_unit_container = fields.Integer(
        string="Product Unit/Container", related="product_id.unit_container", store=True
    )
    unit_container = fields.Float(string="Unit/Container")
    weight = fields.Float(
        compute="_compute_weight",
        store=True,
        digits=KILLING_COST_DIGITS,
    )
    percentage = fields.Float(
        string="%",
        compute="_compute_percentage",
        store=True,
        digits=MRP_PRICE_DIGITS,
    )
    base_price = fields.Float(
        digits=MRP_PRICE_DIGITS,
        compute="_compute_base_price",
        store=True,
    )
    applied_price = fields.Float(digits=MRP_PRICE_DIGITS)
    expense_kg = fields.Boolean(
        string="Cost/Kgm", compute="_compute_expense_kg", store=True
    )
    canal = fields.Boolean(related="product_id.canal", store=True)
    brut = fields.Float()
    pallet = fields.Integer(string="Pallet Qty")
    month_cost = fields.Float(compute="_compute_month_cost", store=True)
    operation_id = fields.Many2one(
        string="Operation",
        comodel_name="mrp.routing.workcenter",
        related="move_id.byproduct_id.operation_id",
        store=True,
    )
    pallet_id = fields.Many2one(
        comodel_name="product.product",
        default=_default_pallet_id,
        domain="[('palet', '=', True)]",
    )
    clean_qty = fields.Float(
        string="Clean",
    )
    clean_performance = fields.Float(compute="_compute_clean_performance", store=True)

    @api.depends(
        "production_id",
        "production_id.move_line_ids",
        "production_id.move_line_ids.clean_qty",
        "quantity",
    )
    def _compute_clean_performance(self):
        for line in self:
            clean_performance = 0
            if (
                line.production_id
                and sum(line.production_id.move_line_ids.mapped("clean_qty")) != 0
            ):
                clean_performance = line.quantity / sum(
                    line.production_id.move_line_ids.mapped("clean_qty")
                )
            line.clean_performance = clean_performance

    @api.depends(
        "production_id",
        "production_id.date_start",
        "move_id",
        "move_id.bom_line_id",
        "move_id.bom_line_id.operation_id",
        "move_id.bom_line_id.operation_id.workcenter_id",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.january",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.february",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.march",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.april",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.may",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.june",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.july",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.august",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.september",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.october",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.november",
        "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.december",
    )
    def _compute_month_cost(self):
        for line in self:
            month_cost = 0
            if line.month_cost:
                month_cost = line.month_cost
            date = line.production_id.date_start
            lock_date = line.company_id.fiscalyear_lock_date
            if (
                date
                and line.move_id
                and line.move_id.byproduct_id
                and line.move_id.byproduct_id.operation_id
                and lock_date
                and date.date() >= lock_date
            ):
                month = date.month
                cost_ids = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids
                monthly_costs = {
                    1: cost_ids.january,
                    2: cost_ids.february,
                    3: cost_ids.march,
                    4: cost_ids.april,
                    5: cost_ids.may,
                    6: cost_ids.june,
                    7: cost_ids.july,
                    8: cost_ids.august,
                    9: cost_ids.september,
                    10: cost_ids.october,
                    11: cost_ids.november,
                    12: cost_ids.december,
                }
                month_cost = monthly_costs.get(month, month_cost)
            line.month_cost = month_cost

    @api.depends(
        "move_id",
        "move_id.bom_line_id",
        "move_id.byproduct_id",
        "move_id.bom_line_id.expense_kg",
        "move_id.byproduct_id.expense_kg",
    )
    def _compute_expense_kg(self):
        for line in self:
            expense_kg = 0
            if line.move_id and line.move_id.bom_line_id:
                expense_kg = line.move_id.bom_line_id.expense_kg
            elif line.move_id and line.move_id.byproduct_id:
                expense_kg = line.move_id.byproduct_id.expense_kg
            line.expense_kg = expense_kg

    @api.depends(
        "production_id.purchase_unit_price",
        "production_id.average_cost",
        "production_id.month_cost",
        "production_id.is_deconstruction",
        "production_id.move_line_ids",
        "production_id.move_line_ids.amount",
        "production_id.move_line_ids.lot_id",
        "lot_id",
    )
    def _compute_base_price(self):
        for line in self:
            cost = 0
            if line.production_id and not line.production_id.date_start:
                raise ValidationError(_("You must introduce the planned date."))
            else:
                if (
                    line.production_id
                    and (line.move_id.bom_line_id)
                    and (line.production_id.is_deconstruction)
                ):
                    cost = line.move_id.bom_line_id.cost
                    if line.expense_kg:
                        cost = (
                            line.production_id.month_cost
                            + (line.production_id.purchase_unit_price)
                        ) * (line.move_id.bom_line_id.coefficient)
                elif line.production_id and line.move_id.byproduct_id:
                    cost = line.move_id.byproduct_id.cost
                    if line.expense_kg:
                        lot_name = line.lot_id.name
                        entry_same_lots = line.production_id.move_line_ids.filtered(
                            lambda c, lot_name=lot_name: c.lot_id.name == lot_name
                        )
                        if (
                            not entry_same_lots
                            or sum(entry_same_lots.mapped("quantity")) == 0
                        ):
                            cost = 0
                        else:
                            entry_cost = sum(entry_same_lots.mapped("amount")) / sum(
                                entry_same_lots.mapped("quantity")
                            )
                            cost = (line.month_cost + entry_cost) * (
                                line.move_id.byproduct_id.coefficient
                            )
            line.base_price = cost
            if not line.applied_price:
                line.applied_price = cost
            if not line.standard_price:
                line.standard_price = cost

    @api.depends("unit", "quantity")
    def _compute_weight(self):
        for line in self:
            weight = 0
            if line.unit != 0:
                weight = line.quantity / line.unit
            line.weight = weight

    @api.depends("quantity", "production_id.origin_qty")
    def _compute_percentage(self):
        for line in self:
            percentage = 0
            if line.production_id.origin_qty != 0:
                percentage = line.quantity * 100 / line.production_id.origin_qty
            line.percentage = percentage

    @api.onchange("brut", "pallet", "container", "pallet_id")
    def onchange_brut(self):
        if self.brut:
            self.quantity = (
                self.brut
                - (self.pallet * self.pallet_id.weight)
                - (self.container * self.production_id.packaging_id.weight)
            )

    @api.onchange("container")
    def onchange_container(self):
        if self.container:
            self.unit = self.product_unit_container * self.container
            self.unit_container = self.product_unit_container

    @api.onchange("unit")
    def onchange_unit(self):
        if self.unit and self.container != 0:
            self.unit_container = self.unit / self.container
        if self.unit and self.product_id and self.product_id.asphyxiated:
            self.quantity = self.unit * self.production_id.average_weight

    @api.onchange("base_price")
    def onchange_base_price(self):
        self.ensure_one()
        if self.base_price:
            self.applied_price = self.base_price
            self.onchange_applied_price()

    @api.onchange("applied_price")
    def onchange_applied_price(self):
        if self.applied_price:
            self.standard_price = self.applied_price
            self.onchange_standard_price()
