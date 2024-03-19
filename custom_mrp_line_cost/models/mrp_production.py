# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    origin_qty = fields.Float(
        string="Origin Kg")
    dest_qty = fields.Float(
        string="Dest Kg")
    purchase_price = fields.Float(
        string="Purchase Amount")
    purchase_unit_price = fields.Float(
        string="Purchase Unit Price")
    price_difference = fields.Float(
        string="Price Difference",
        )
    canal_weight = fields.Float(
        string="Canal Average Weight",
        compute="_compute_canal_weight",
        store=True,
        digits="Killing Cost Decimal Precision")
    rto_canal = fields.Float(
        string="Rto. Canal",
        compute="_compute_rto_canal",
        store=True)
    canal_cost = fields.Float(
        string="Canal Cost",
        digits="Killing Cost Decimal Precision",
        compute="_compute_canal_cost",
        store=True)
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id)
    month_cost = fields.Float(
        string="Expense/kg",
        digits="Killing Cost Decimal Precision",
        compute="_compute_month_cost",
        store=True
        )
    move_to_do_ids = fields.Many2many(
        string="Moves To Do",
        comodel_name="stock.move",
        compute="_compute_move_to_do_ids"
        )
    move_line_to_do_ids = fields.Many2many(
        string="Move Lines To Do",
        comodel_name="stock.move.line",
        compute="_compute_move_line_to_do_ids"
        )
    picking_to_do_ids = fields.Many2many(
        string="Pickings To Do",
        comodel_name="stock.picking",
        compute="_compute_picking_to_do_ids"
        )
    pallet_id = fields.Many2one(
        string="Pallet",
        comodel_name="product.product",
        related="bom_id.pallet_id",
        store=True)
    packaging_id = fields.Many2one(
        string="Packaging",
        comodel_name="product.product",
        related="bom_id.packaging_id",
        store=True)
    average_cost = fields.Float(
        string="Averga Cost",
        compute="_compute_average_cost",
        store=True)
    cost = fields.Float(
        string="Cost",
        compute="_compute_cost",
        store=True)
    entry_total_amount = fields.Float(
        string="Entry Total Amount",
        compute="_compute_entry_total_amount",
        store=True)
    output_total_amount = fields.Float(
        string="Output Total Amount")
    consume_qty = fields.Float(
        string="Consumed Qty",
        compute="_compute_consume_qty",
        store=True)

    @api.depends("move_line_ids", "move_line_ids.qty_done",
                 "product_uom_id", "move_line_ids.product_uom_id")
    def _compute_consume_qty(self):
        for production in self:
            production.consume_qty = sum(
                production.move_line_ids.filtered(
                    lambda c: c.location_id == (
                        production.location_dest_id
                    ) and c.product_uom_id == production.product_uom_id
                ).mapped("qty_done")
            )

    @api.depends("purchase_price", "month_cost", "origin_qty")
    def _compute_cost(self):
        for production in self:
            production.cost = production.purchase_price + (
                production.month_cost * production.origin_qty)

    @api.depends("move_line_ids", "move_line_ids.amount")
    def _compute_entry_total_amount(self):
        for line in self:
            if line.move_line_ids:
                line.entry_total_amount = sum(
                    self.move_line_ids.mapped("amount"))

    @api.depends("finished_move_line_ids", "finished_move_line_ids.amount")
    def _compute_output_total_amount(self):
        for production in self:
            production.output_total_amount = sum(
                production.finished_move_line_ids.mapped("amount"))

    @api.depends("move_line_ids", "move_line_ids.qty_done",
                 "move_line_ids.amount")
    def _compute_average_cost(self):
        for line in self:
            average_cost = 0
            if sum(line.move_line_ids.filtered(
                lambda c: c.location_id == line.location_src_id).mapped(
                    "qty_done")) != 0:
                average_cost = sum(
                    line.move_line_ids.filtered(
                        lambda c: c.location_id == (
                            line.location_src_id)).mapped("amount")) / sum(
                                line.move_line_ids.filtered(
                                    lambda c: c.location_id == (
                                        line.location_src_id)).mapped(
                                            "qty_done"))
            line.average_cost = average_cost

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

    @api.depends("workorder_ids", "workorder_ids.workcenter_id",
                 "workorder_ids.workcenter_id.cost_ids.january",
                 "workorder_ids.workcenter_id.cost_ids.february",
                 "workorder_ids.workcenter_id.cost_ids.march",
                 "workorder_ids.workcenter_id.cost_ids.april",
                 "workorder_ids.workcenter_id.cost_ids.may",
                 "workorder_ids.workcenter_id.cost_ids.june",
                 "workorder_ids.workcenter_id.cost_ids.july",
                 "workorder_ids.workcenter_id.cost_ids.august",
                 "workorder_ids.workcenter_id.cost_ids.september",
                 "workorder_ids.workcenter_id.cost_ids.october",
                 "workorder_ids.workcenter_id.cost_ids.november",
                 "workorder_ids.workcenter_id.cost_ids.december",
                 "date_planned_start")
    def _compute_month_cost(self):
        for line in self:
            line.month_cost = 0
            if line.date_planned_start and line.workorder_ids:
                month = line.date_planned_start.month
                if month == 1:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.january)
                if month == 2:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.february)
                if month == 3:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.march)
                if month == 4:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.april)
                if month == 5:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.may)
                if month == 6:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.june)
                if month == 7:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.july)
                if month == 8:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.august)
                if month == 9:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.september
                        )
                if month == 10:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.october)
                if month == 11:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.november)
                if month == 12:
                    line.month_cost = (
                        line.workorder_ids[:1].workcenter_id.cost_ids.december)

    def button_mark_done(self):
        result = super(MrpProduction, self).button_mark_done()
        self.button_calculate_costs()
        return result

    def button_calculate_costs(self):
        for production in self:
            qty = []
            lots = []
            if production.is_deconstruction and (
                    production.move_line_ids):
                dif = production.cost - production.entry_total_amount
                if dif != 0:
                    for line in production.move_line_ids:
                        line.onchange_applied_price()
                        if not line.move_id:
                            line.move_id = production.move_raw_ids.filtered(
                                lambda c: c.product_id == line.product_id).id
                        if line.lot_id and line.lot_id not in lots:
                            lots.append(line.lot_id)
                            qty.append(
                                sum(production.move_line_ids.filtered(
                                    lambda c: c.lot_id == line.lot_id).mapped(
                                        "qty_done")))
                    i = qty.index(max(qty))
                    max_lot = lots[i]
                    max_qty = qty[i]
                    if max_lot and max_qty:
                        lot_lines = production.move_line_ids.filtered(
                            lambda c: c.lot_id == max_lot)
                        amount = dif + sum(lot_lines.mapped("amount"))
                        price = amount / max_qty
                        for max_line in lot_lines:
                            max_line.applied_price = price
                            max_line.onchange_applied_price()
            elif not production.is_deconstruction and (
                production.average_cost) and (
                    production.finished_move_line_ids):
                for line in production.finished_move_line_ids:
                    line.applied_price = line.base_price
                    line.standard_price = line.applied_price
                dif = production.average_cost + (
                    production.month_cost * production.consume_qty) - (
                        production.output_total_amount)
                if dif != 0:
                    for line in production.finished_move_line_ids:
                        if line.lot_id and line.lot_id not in lots:
                            lots.append(line.lot_id)
                            qty.append(
                                sum(production.finished_move_line_ids.filtered(
                                    lambda c: c.lot_id == line.lot_id).mapped(
                                        "qty_done")))
                    i = qty.index(max(qty))
                    if i:
                        max_lot = lots[i]
                        max_qty = qty[i]
                        if max_lot and max_qty:
                            lot_lines = (
                                production.finished_move_line_ids.filtered(
                                    lambda c: c.lot_id == max_lot))
                            amount = dif + sum(lot_lines.mapped("amount"))
                            price = amount / max_qty
                            for max_line in lot_lines:
                                max_line.applied_price = price
                                max_line.onchange_applied_price()

    @api.depends("move_line_ids", "move_line_ids.canal",
                 "move_line_ids.qty_done")
    def _compute_canal_weight(self):
        for line in self:
            canal_weight = 0
            canal_lines = line.move_line_ids.filtered(
                lambda c: c.canal is True)
            canal_weight = sum(canal_lines.mapped("qty_done"))
            canal_unit = sum(canal_lines.mapped("unit"))
            if canal_unit != 0:
                canal_weight = canal_weight / canal_unit
            line.canal_weight = canal_weight

    @api.depends("move_line_ids", "move_line_ids.canal",
                 "move_line_ids.percentage")
    def _compute_rto_canal(self):
        for line in self:
            rto_canal = 0
            canal_lines = line.move_line_ids.filtered(
                lambda c: c.canal is True)
            if canal_lines:
                rto_canal = sum(canal_lines.mapped("percentage"))
            line.rto_canal = rto_canal

    @api.depends("move_line_ids", "move_line_ids.canal",
                 "move_line_ids.qty_done", "move_line_ids.amount")
    def _compute_canal_cost(self):
        for line in self:
            canal_cost = 0
            if line.move_line_ids:
                canal_lines = line.move_line_ids.filtered(
                    lambda c: c.canal is True)
                if canal_lines and sum(canal_lines.mapped("weight")) != 0:
                    canal_cost = sum(
                        canal_lines.mapped("amount"))/sum(
                            canal_lines.mapped("qty_done"))
            line.canal_cost = canal_cost

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

    def action_view_finished_move_line_ids(self):
        context = self.env.context.copy()
        context.update({
            "default_production_id": self.id,
            "default_location_id": self.production_location_id.id,
            "default_location_dest_id": self.location_dest_id.id,
            "default_company_id": self.company_id.id,
            "company_id": self.company_id.id,
        })
        return {
            "name": _("Outputs"),
            "view_mode": "tree",
            "view_id": self.env.ref(
                "custom_mrp_line_cost.production_finished_move_line_ids_tree_view"
            ).id,
            "res_model": "stock.move.line",
            "domain": [("id", "in", self.finished_move_line_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }

    def action_view_move_line_ids(self):
        context = self.env.context.copy()
        context.update({
            "production_id": self.id,
            "default_production_id": self.id,
            "location_id": self.location_src_id.id,
            "location_dest_id": self.production_location_id.id,
            "company_id": self.company_id.id,
            "default_company_id": self.company_id.id,
        })
        return {
            "name": _("Entries"),
            "view_mode": "tree",
            "view_id": self.env.ref(
                "custom_mrp_line_cost.production_move_line_ids_tree_view"
            ).id,
            "res_model": "stock.move.line",
            "domain": [("id", "in", self.move_line_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }
