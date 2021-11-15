# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _
from odoo.tools import float_round


class NestedNewLine(models.TransientModel):
    _name = "nested.new.line"
    _description = "Wizard to nest workorders"
    _rec_name = "nest_code"

    nest_code = fields.Char(string="Nest Name", required=True)
    product_id = fields.Many2one(comodel_name="product.product")
    possible_product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_possible_products")
    line_ids = fields.One2many(
        comodel_name="nested.lines.info",
        inverse_name="nest_id",
        string="Nest Lines")
    filtered_line_ids = fields.One2many(
        comodel_name="nested.lines.info",
        inverse_name="nest_id",
        string="Filtered Nest Lines")

    def _workorders_domain(self):
        return [
            ("id", "in", self.env.context.get("active_ids")),
            ("main_product_id", "!=", False),
            ("workcenter_id", "!=", False),
            ("state", 'not in', ["done", "cancel"]),
        ]

    def _prepare_lines(self, product=False):
        lines = []
        if self.env.context.get("active_model") == "mrp.workorder":
            domain = self._workorders_domain()
            workorders = self.env["mrp.workorder"].search(domain)
            line_obj = self.env["nested.lines.info"]
            if product:
                workorders = workorders.filtered(
                    lambda w: w.product_id == product)
            for wo in workorders:
                line = line_obj.new({
                    "workorder_id": wo.id,
                })
                line._onchange_workorder_id()
                line_data = line._convert_to_write(line._cache)
                lines.append((0, 0, line_data))
        return lines

    @api.model
    def default_get(self, values):
        res = super().default_get(values)
        domain = self._workorders_domain()
        workorders = self.env["mrp.workorder"].search(domain)
        products = workorders.mapped("product_id")
        if len(products) == 1:
            res.update({
                "product_id": products.id,
            })
        res.update({
            "line_ids": self._prepare_lines(),
        })
        return res

    @api.depends("line_ids", "line_ids.workorder_id",
                 "line_ids.workorder_id.product_id")
    def _compute_possible_products(self):
        for record in self:
            record.possible_product_ids = [
                (6, 0, record.mapped("line_ids.workorder_id.product_id").ids)]

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.ensure_one()
        lines = self.line_ids | self.filtered_line_ids
        self.filtered_line_ids = lines.filtered(
            lambda l: l.product_id == self.product_id)
        self.line_ids = lines.filtered(
            lambda l: l.product_id != self.product_id)

    def action_done(self):
        main_product_workcenter = {}
        lines = self.line_ids | self.filtered_line_ids
        for line in lines:
            wo = line.workorder_id
            if line.qty_producing + wo.qty_produced > wo.qty_production:
                raise exceptions.ValidationError(
                    _("the quantity to be produced must be less than or "
                      "equal to quantity produced"))
            workcenter_dict = main_product_workcenter.get(
                wo.main_product_id.id)
            if workcenter_dict:
                res_workorders = workcenter_dict.get(
                    wo.workcenter_id.id, self.env['mrp.workorder'])
                res_workorders |= line
                workcenter_dict.update({
                    wo.workcenter_id.id: res_workorders,
                })
            else:
                main_product_workcenter.update({
                    wo.main_product_id.id: {
                        wo.workcenter_id.id: line,
                    }})
        for main_id, workcenters in main_product_workcenter.items():
            for workcenter, lines in workcenters.items():
                new_lines = [
                    (0, 0, {
                        "workorder_id": line.workorder_id.id,
                        "qty_producing": line.qty_producing,
                        "state": line.workorder_id.state})
                    for line in lines]
                self.env["mrp.workorder.nest"].create({
                    "code": self.nest_code,
                    "main_product_id": main_id,
                    "workcenter_id": workcenter,
                    "nested_line_ids": new_lines,
                })


class NestedLinesInfo(models.TransientModel):
    _name = "nested.lines.info"
    _description = "Lines of wizard to nest workorders"

    nest_id = fields.Many2one(
        comodel_name="nested.new.line",
        string="Nest",
        required=True)
    workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Workorder",
        required=True)
    product_id = fields.Many2one(
        comodel_name="product.product")
    qty_producing = fields.Float(
        string="Quantity to Nest")
    qty_production = fields.Float(
        string="Original Production Quantity")
    qty_produced = fields.Float(
        string="Produced Quantity",
        digits="Product Unit of Measure",
        help="The number of products already handled by this work order")
    qty_nested = fields.Float(
        string="Already Nested Quantity")
    # finished_qty_nested = fields.Float(
    #     string="Finished Nested Quantity")
    qty_nested_remaining = fields.Float(
        string="Quantity To Be Nested")
    qty_remaining = fields.Float(
        string="Quantity To Be Produced",
        digits="Product Unit of Measure")

    @api.onchange("workorder_id")
    def _onchange_workorder_id(self):
        for record in self:
            wo = record.workorder_id
            record.product_id = wo.product_id
            record.qty_production = wo.qty_production
            record.qty_produced = wo.qty_produced
            record.qty_nested = wo.qty_nested
            # record.finished_qty_nested = wo.finished_qty_nested
            qty_remaining = qty_nested_remaining = 0.0
            if wo:
                production_qty = wo._get_real_uom_qty(record.qty_production)
                qty_nested = wo._get_real_uom_qty(record.qty_nested)
                rounding = wo.production_id.product_uom_id.rounding
                qty_remaining = float_round(
                    (production_qty - record.qty_produced),
                    precision_rounding=rounding)
                qty_nested_remaining = float_round(
                    qty_remaining - (qty_nested - record.qty_produced),
                    precision_rounding=rounding)
            record.qty_remaining = qty_remaining
            record.qty_nested_remaining = qty_nested_remaining
            if wo.workcenter_id.copy_production_qty:
                record.qty_producing = wo.qty_production
