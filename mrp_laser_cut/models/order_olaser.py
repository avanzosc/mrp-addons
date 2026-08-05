# Copyright 2026 Inael
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class OrderOlaser(models.Model):
    _name = "order.olaser"
    _inherit = ["mail.thread"]
    _description = "Laser Cutting Order"

    _sql_constraints = [
        (
            "order_olaser_unique_code",
            "UNIQUE (name)",
            "The order number must be unique!",
        ),
    ]

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    date = fields.Datetime(required=True, default=fields.Datetime.now, copy=False)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmado", "Confirmed"),
            ("proceso", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        compute="_compute_state",
        store=True,
        tracking=True,
        help="Derived from the state of the manufacturing order and its "
        "backorders: Draft > Confirmed > In Progress > Done > Cancelled, "
        "checked in that order of priority.",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Raw Material",
        required=True,
    )
    cantidad = fields.Float(
        string="Quantity",
        required=True,
        default=0,
        compute="_compute_cantidad",
        store=True,
        readonly=False,
        help="Number of sheets. Manually set until a manufacturing order "
        "exists; from then on, it is kept in sync with the total quantity "
        "to produce across the whole manufacturing order chain (initial "
        "order and backorders), so it always reflects what is actually "
        "being produced.",
    )
    terminado = fields.Float(
        string="Produced Quantity",
        compute="_compute_terminado",
        store=True,
        help="Sum of the quantity produced across all the manufacturing "
        "orders related to this laser cutting order.",
    )
    peso_mp = fields.Float(
        string="Unit Weight (kg)",
        required=True,
        help="Weight of one raw material sheet.",
    )
    es_retal = fields.Boolean(
        string="Is Scrap",
        help="If checked, the scrap product is consumed instead of the "
        "raw material.",
    )
    listas_ids = fields.One2many(
        comodel_name="order.olaser.lista",
        inverse_name="olaser_id",
        string="Distribution",
        copy=True,
    )
    olaser_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="olaser_id",
        string="Raw Material Moves",
        help="Legacy field from the workflow prior to native manufacturing "
        "orders: raw material consumption moves for historical orders. "
        "New orders access these through the manufacturing order instead.",
    )
    lista_olaser_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="lista_olaser_id",
        string="Finished Product Moves",
        help="Legacy field from the workflow prior to native manufacturing "
        "orders: finished product moves for historical orders. New orders "
        "access these through the manufacturing order instead.",
    )
    laser_tiempos_ids = fields.One2many(
        comodel_name="order.olaser.tiempos",
        inverse_name="laser_tiempos_id",
        string="Times",
    )
    rechazos_ids = fields.One2many(
        comodel_name="order.olaser.rechazo",
        inverse_name="olaser_id",
        string="Rejects",
    )

    scrap_product_id = fields.Many2one(
        comodel_name="product.product",
        default=lambda self: self.env.company.laser_scrap_product_id,
        help="Generic scrap/offcut product consumed instead of the raw "
        "material when this order uses scrap.",
    )
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
        required=True,
        default=lambda self: self.env.company.laser_bom_id,
        help="Bill of Materials of the generic product used to create the "
        "manufacturing order.",
    )
    unit_time = fields.Float(
        string="Time per Sheet",
        help="Estimated time, in minutes, to cut one sheet.",
    )
    total_time = fields.Float(
        compute="_compute_total_time",
        store=True,
        help="Time per Sheet * Quantity. Set as the expected duration of "
        "the work order created on the manufacturing order.",
    )
    actual_time = fields.Float(
        compute="_compute_actual_time",
        store=True,
        help="Real duration of the work orders of all the manufacturing "
        "orders related to this laser cutting order (initial order and "
        "backorders).",
    )
    total_consumed_quantity = fields.Float(
        compute="_compute_amounts",
        store=True,
        help="Sum of the raw material quantity consumed across all the "
        "manufacturing orders related to this laser cutting order.",
    )
    actual_consumed_quantity = fields.Float(
        compute="_compute_amounts",
        store=True,
        help="Sum of the weight of all the byproducts actually produced "
        "across all the manufacturing orders related to this laser cutting "
        "order.",
    )
    estimated_waste = fields.Float(
        compute="_compute_estimated_waste",
        help="Quantity * (Unit Weight - sum of the line weight of all the "
        "distribution lines).",
    )
    actual_waste = fields.Float(
        compute="_compute_amounts",
        store=True,
        help="Total Consumed Quantity - Actual Consumed Quantity.",
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
        readonly=True,
        copy=False,
    )
    production_count = fields.Integer(
        string="Manufacturing Order Count", compute="_compute_production_count"
    )
    workorder_count = fields.Integer(
        string="Work Order Count", compute="_compute_workorder_count"
    )

    def _get_productions(self):
        self.ensure_one()
        return self.production_id.procurement_group_id.mrp_production_ids

    @api.depends(
        "production_id.state",
        "production_id.procurement_group_id.mrp_production_ids.state",
    )
    def _compute_state(self):
        for order in self:
            productions = order._get_productions()
            if not productions:
                order.state = "draft"
                continue
            states = set(productions.mapped("state"))
            if "draft" in states:
                order.state = "draft"
            elif states & {"progress", "to_close"}:
                order.state = "proceso"
            elif "done" in states and "confirmed" in states:
                order.state = "proceso"
            elif "done" in states:
                order.state = "done"
            elif "confirmed" in states:
                order.state = "confirmado"
            else:
                order.state = "cancel"

    @api.depends(
        "production_id.product_qty",
        "production_id.procurement_group_id.mrp_production_ids.product_qty",
        "production_id.procurement_group_id.mrp_production_ids.state",
    )
    def _compute_cantidad(self):
        for order in self:
            productions = order._get_productions().filtered(
                lambda p: p.state != "cancel"
            )
            if productions:
                order.cantidad = sum(productions.mapped("product_qty"))

    @api.depends("unit_time", "cantidad")
    def _compute_total_time(self):
        for order in self:
            order.total_time = order.unit_time * order.cantidad

    @api.depends(
        "production_id.workorder_ids.duration",
        "production_id.procurement_group_id.mrp_production_ids.workorder_ids.duration",
    )
    def _compute_actual_time(self):
        for order in self:
            productions = order._get_productions()
            order.actual_time = sum(productions.workorder_ids.mapped("duration"))

    def _get_consumed_material(self):
        self.ensure_one()
        return self.scrap_product_id if self.es_retal else self.product_id

    @api.depends(
        "production_id.qty_produced",
        "production_id.procurement_group_id.mrp_production_ids.qty_produced",
    )
    def _compute_terminado(self):
        for order in self:
            productions = order._get_productions()
            order.terminado = sum(productions.mapped("qty_produced"))

    @api.depends(
        "production_id.move_raw_ids.state",
        "production_id.move_raw_ids.quantity",
        "production_id.move_finished_ids.state",
        "production_id.move_finished_ids.quantity",
        "production_id.procurement_group_id.mrp_production_ids.move_raw_ids.state",
        "production_id.procurement_group_id.mrp_production_ids.move_raw_ids.quantity",
        "production_id.procurement_group_id.mrp_production_ids.move_finished_ids.state",
        "production_id.procurement_group_id.mrp_production_ids.move_finished_ids.quantity",
    )
    def _compute_amounts(self):
        for order in self:
            productions = order._get_productions()
            material = order._get_consumed_material()
            raw_moves = productions.move_raw_ids.filtered(
                lambda m, material=material: (
                    m.product_id == material and m.state == "done"
                )
            )
            byproduct_moves = productions.move_byproduct_ids.filtered(
                lambda m: m.state == "done"
            )
            bom_qty_by_product = {
                line.product_id: line.cantidad_consumo for line in order.listas_ids
            }
            order.total_consumed_quantity = sum(raw_moves.mapped("quantity"))
            order.actual_consumed_quantity = sum(
                move.quantity * bom_qty_by_product.get(move.product_id, 0)
                for move in byproduct_moves
            )
            order.actual_waste = (
                order.total_consumed_quantity - order.actual_consumed_quantity
            )

    @api.depends("cantidad", "peso_mp", "listas_ids.cantidad_consumo_total")
    def _compute_estimated_waste(self):
        for order in self:
            lines_weight = sum(order.listas_ids.mapped("cantidad_consumo_total"))
            order.estimated_waste = order.cantidad * (order.peso_mp - lines_weight)

    @api.depends("production_id")
    def _compute_production_count(self):
        for order in self:
            order.production_count = len(order._get_productions())

    @api.depends("production_id")
    def _compute_workorder_count(self):
        for order in self:
            order.workorder_count = len(order._get_productions().workorder_ids)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.peso_mp = self.product_id.weight

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("order.olaser") or "New"
                )
        return super().create(vals_list)

    def unlink(self):
        for order in self:
            if order.production_id:
                raise UserError(
                    _(
                        "You cannot delete a laser cutting order that has a "
                        "manufacturing order."
                    )
                )
        return super().unlink()

    def _prepare_production_values(self):
        self.ensure_one()
        bom = self.bom_id
        product = bom.product_id or bom.product_tmpl_id.product_variant_id
        Production = self.env["mrp.production"]
        picking_type = bom.picking_type_id or Production.browse(
            Production._get_default_picking_type_id(self.env.company.id)
        )
        location_src = (
            picking_type.default_location_src_id
            or self.env["stock.warehouse"]
            .search([("company_id", "=", self.env.company.id)], limit=1)
            .lot_stock_id
        )
        location_dest = picking_type.default_location_dest_id or location_src
        return {
            "bom_id": bom.id,
            "product_id": product.id,
            "product_qty": self.cantidad,
            "origin": self.name,
            "laser_order_id": self.id,
            "picking_type_id": picking_type.id,
            "location_src_id": location_src.id,
            "location_dest_id": location_dest.id,
        }

    def _prepare_consumption_move_values(self, production):
        self.ensure_one()
        material = self._get_consumed_material()
        return {
            "raw_material_production_id": production.id,
            "product_id": material.id,
            "product_uom_qty": self.cantidad * self.peso_mp,
            "product_uom": material.uom_id.id,
            "name": material.display_name,
        }

    def _prepare_byproduct_move_values(self, production, line):
        return {
            "production_id": production.id,
            "product_id": line.product_id.id,
            "product_uom_qty": line.cantidad_chapa_total,
            "product_uom": line.product_id.uom_id.id,
            "name": line.product_id.display_name,
        }

    def action_create_production(self):
        self.ensure_one()
        if self.production_id and self.production_id.state != "cancel":
            raise UserError(_("This order already has a manufacturing order."))
        if not self.listas_ids:
            raise UserError(
                _(
                    "You need at least one distribution line to create a "
                    "manufacturing order."
                )
            )
        production = self.env["mrp.production"].create(
            self._prepare_production_values()
        )
        production.workorder_ids.write({"duration_expected": self.total_time})
        production.action_confirm()
        moves = self.env["stock.move"].create(
            [self._prepare_consumption_move_values(production)]
            + [
                self._prepare_byproduct_move_values(production, line)
                for line in self.listas_ids
            ]
        )
        moves._action_confirm()
        self.production_id = production.id
        return self.action_view_productions()

    def action_cancel(self):
        for order in self:
            productions = order._get_productions()
            done_moves = (
                productions.move_raw_ids | productions.move_finished_ids
            ).filtered(lambda m: m.state == "done")
            if done_moves:
                raise UserError(
                    _(
                        "You cannot cancel a laser cutting order that "
                        "already has completed stock moves; cancel the "
                        "manufacturing order directly instead."
                    )
                )
            productions.filtered(lambda p: p.state != "cancel").action_cancel()
        return True

    def action_view_productions(self):
        self.ensure_one()
        productions = self._get_productions()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.mrp_production_action"
        )
        action["domain"] = [("id", "in", productions.ids)]
        action["context"] = {}
        if len(productions) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = productions.id
        return action

    def action_view_workorders(self):
        self.ensure_one()
        productions = self._get_productions()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.action_mrp_workorder_production_specific"
        )
        action["domain"] = [("production_id", "in", productions.ids)]
        return action

    def action_view_move_lines(self):
        self.ensure_one()
        productions = self._get_productions()
        moves = (
            productions.move_raw_ids
            | productions.move_finished_ids
            | self.olaser_ids
            | self.lista_olaser_ids
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.stock_move_line_action"
        )
        action["domain"] = [("move_id", "in", moves.ids)]
        action["context"] = {}
        return action
