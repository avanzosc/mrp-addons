# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp


class MrpProductionProductLine(models.Model):
    _name = "mrp.production.product.line"
    _description = "Production Scheduled Product"

    name = fields.Char(string="Name", required=True, readonly=True,
                       states={"draft": [("readonly", False)]})
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True,
        readonly=True, states={"draft": [("readonly", False)]})
    product_qty = fields.Float(
        string="Product Quantity",
        digits=dp.get_precision("Product Unit of Measure"), required=True,
        readonly=True, states={"draft": [("readonly", False)]})
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="Unit of Measure", required=True,
        readonly=True, states={"draft": [("readonly", False)]})
    production_id = fields.Many2one(
        comodel_name="mrp.production", string="Production Order",
        required=True, ondelete="cascade", readonly=True,
        states={"draft": [("readonly", False)]}, auto_join=True)
    bom_line_id = fields.Many2one(
        comodel_name="mrp.bom.line", string="Bom Line", readonly=True,
        states={"draft": [("readonly", False)]})
    date_planned_start = fields.Datetime(
        string="Deadline Start", store=True,
        related="production_id.date_planned_start")
    state = fields.Selection(
        string="Production State",
        selection=[("draft", "Draft"),
                   ("confirmed", "Confirmed"),
                   ("planned", "Planned"),
                   ("progress", "In Progress"),
                   ("done", "Done"),
                   ("cancel", "Cancelled")],
        compute="_compute_state",
        store=True)
    production_product_id = fields.Many2one(
        string="Product to Produce",
        related="production_id.product_id",
        store=True)

    @api.depends("production_id.state")
    def _compute_state(self):
        for line in self:
            line.state = line.production_id.state

    @api.onchange("product_id", "bom_line_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.bom_line_id.product_uom_id or self.product_id.uom_id
            self.name = self.product_id.name or self.bom_line_id.product_tmpl_id.name
            try:
                self.product_tmpl_id = self.product_id.product_tmpl_id
            except Exception:
                # This is in case mrp_product_variants module is not installed
                pass


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    product_line_ids = fields.One2many(
        comodel_name="mrp.production.product.line",
        inverse_name="production_id", string="Scheduled goods")
    state = fields.Selection(selection_add=[("draft", "Draft")],
                             default="draft")
    active = fields.Boolean(string="Active", default=False)

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        for production in self:
            res = production._prepare_lines()
            prod_lines = []
            for bom_line, line_data in res:
                prod_lines.append((0, 0, line_data))
            production.update({
                "product_line_ids": [
                    (2, line.id) for line in production.product_line_ids],
            })
            production.update({
                "product_line_ids": prod_lines,
            })

    def _get_raw_move_dict(self, product_line):
        self.ensure_one()
        routing = self.routing_id or self.bom_id.routing_id
        source_location = (
            routing and routing.location_id or self.location_src_id)
        original_qty = self.product_qty - self.qty_produced
        return {
            "sequence": product_line.bom_line_id.sequence,
            "name": self.name,
            "date": self.date_planned_start,
            "date_expected": self.date_planned_start,
            "bom_line_id": product_line.bom_line_id.id,
            "product_id": product_line.product_id.id,
            "product_uom_qty": product_line.product_qty,
            "product_uom": product_line.product_uom_id.id,
            "location_id": source_location.id,
            "location_dest_id":
                self.product_id.property_stock_production.id,
            "raw_material_production_id": self.id,
            "company_id": self.company_id.id,
            "operation_id": product_line.bom_line_id.operation_id.id,
            "price_unit": product_line.product_id.standard_price,
            "procure_method": "make_to_stock",
            "origin": self.name,
            "warehouse_id": source_location.get_warehouse().id,
            "group_id": self.procurement_group_id.id,
            "propagate": self.propagate,
            "unit_factor": product_line.product_qty / original_qty,
            "production_product_line_id": product_line.id,
        }

    def _generate_raw_moves(self, exploded_lines):
        self.ensure_one()
        moves = self.env["stock.move"]
        if not self.product_line_ids:
            return super(MrpProduction,
                         self.filtered(
                             lambda x: x.state != "draft")
                         )._generate_raw_moves(exploded_lines)
        for line in self.product_line_ids:
            data = self._get_raw_move_dict(line)
            moves += moves.create(data)
        return moves

    def _generate_finished_moves(self):
        """Avoid draft moves generation of draft state mo"""
        super(MrpProduction,
              self.filtered(lambda x: x.state != "draft"))._generate_finished_moves()

    @api.multi
    def _generate_moves(self):
        """Avoid draft moves generation of draft state mo"""
        super(MrpProduction,
              self.filtered(lambda x: x.state != "draft"))._generate_moves()

    @api.multi
    def button_confirm(self):
        products = self.product_line_ids.mapped("product_id.id")
        if not all(products) or not products:
            raise exceptions.Warning(
                _("Not all scheduled products has a product"))
        orders_to_confirm = self.filtered(lambda order: order.state == "draft")
        orders_to_confirm.write({
            "state": "confirmed",
            "active": "True",
        })
        return orders_to_confirm._generate_moves()

    @api.multi
    def _action_compute_lines(self):
        """ Compute product_lines from BoM structure
        @return: product_lines
        """
        results = []
        prod_line_obj = self.env["mrp.production.product.line"]
        for production in self:
            # unlink product_lines
            production.product_line_ids.sudo().unlink()
            res = production._prepare_lines()
            results = res  # product_lines
            # reset product_lines in production order
            for bom_line, line_data in res:
                prod_line_obj.create(line_data)
        return results

    @api.multi
    def _prepare_lines(self):
        # search BoM structure and route
        lines_done = []
        if self.product_id:
            bom_obj = self.env["mrp.bom"]
            product_line_obj = self.env["mrp.production.product.line"]
            bom_point = self.bom_id
            if not bom_point:
                bom_point = bom_obj._bom_find(product=self.product_id)
                if bom_point:
                    routing = bom_point.routing_id
                    self.write({
                        "bom_id": bom_point.id,
                        "routing_id": routing.id,
                    })

            if not bom_point:
                raise exceptions.MissingError(
                    _("Cannot find a bill of material for this product."))

            # get components from BoM structure
            factor = self.product_uom_id._compute_quantity(
                self.product_qty, bom_point.product_uom_id)
            boms_done, lines_done = bom_point.explode(
                self.product_id, factor / bom_point.product_qty)
            for bom_line, line_data in lines_done:
                prod_line_vals = {
                    "product_id": bom_line.product_id.id,
                    "product_qty": line_data["qty"],
                    "bom_line_id": bom_line.id,
                    "production_id": self.id,
                }
                new_line = product_line_obj.new(prod_line_vals)
                for onchange_method in new_line._onchange_methods["product_id"]:
                    onchange_method(new_line)
                line_data.update(product_line_obj._convert_to_write(new_line._cache))
        return lines_done

    @api.multi
    def action_compute(self):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        return len(self._action_compute_lines())

    def open_table_location(self):
        res = self.env["stock.quantity.history"].create({
            "compute_at_date": 0
        }).open_table()
        product_ids = self.product_line_ids.mapped("product_id").ids
        res["domain"] = [("product_id", "in", product_ids)]
        return res
