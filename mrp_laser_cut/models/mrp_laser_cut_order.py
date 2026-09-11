# Copyright 2026 Inael
# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpLaserCutOrder(models.Model):
    _name = "mrp.laser.cut.order"
    _description = "Laser Cutting Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    _sql_constraints = [
        (
            "name_unique",
            "UNIQUE (name)",
            "The laser cutting order number must be unique.",
        ),
    ]

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        help="Sequence-generated identifier of the laser cutting order.",
    )
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        copy=False,
        help="Date the laser cutting order was registered.",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        compute="_compute_state",
        store=True,
        readonly=False,
        tracking=True,
        help="Overall status derived from the manufacturing order and its "
        "backorders: Draft while any of them is still a draft; In Progress "
        "once cutting has started or some are done while others are not; Done "
        "when they are all done; Confirmed when they are all confirmed but "
        "none has started; Cancelled otherwise. Editable so an order recorded "
        "without a manufacturing order can still carry its real status.",
    )
    raw_material_id = fields.Many2one(
        comodel_name="product.product",
        string="Raw Material",
        required=True,
        help="Product consumed and cut by the order. The finished products "
        "obtained from it are listed on the distribution lines.",
    )
    material_unit_weight = fields.Float(
        string="Unit Weight",
        required=True,
        compute="_compute_material_unit_weight",
        precompute=True,
        store=True,
        readonly=False,
        help="Weight of a single unit of raw material, in the weight unit of "
        "measure of the database. Defaults to the weight of the raw material "
        "product and stays in sync with it until a manufacturing order "
        "exists; it can be overridden by hand.",
    )
    material_qty = fields.Float(
        string="Quantity",
        required=True,
        default=1,
        compute="_compute_material_qty",
        store=True,
        readonly=False,
        help="Number of raw material units to cut. Set by hand until a "
        "manufacturing order exists; from then on it mirrors the total "
        "quantity to produce across the whole manufacturing order chain, so "
        "it always reflects what is really being produced.",
    )
    produced_qty = fields.Float(
        string="Produced",
        compute="_compute_produced_qty",
        store=True,
        readonly=False,
        help="Raw material units already produced, summed across every "
        "manufacturing order linked to this laser cutting order. Editable so "
        "an order recorded without a manufacturing order can still carry the "
        "quantity it really produced.",
    )
    use_offcut = fields.Boolean(
        help="When set, the order consumes the generic offcut (remnant) "
        "product instead of a full unit of raw material.",
    )
    offcut_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Offcut Product",
        default=lambda self: self.env.company.laser_offcut_product_id,
        help="Generic remnant product consumed instead of the raw material "
        "when the order is flagged to use offcut material.",
    )
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
        required=True,
        default=lambda self: self.env.company.laser_bom_id,
        help="Bill of Materials used to create the manufacturing order. Its "
        "product is the generic item manufactured by every laser cutting "
        "order.",
    )
    line_ids = fields.One2many(
        comodel_name="mrp.laser.cut.order.line",
        inverse_name="order_id",
        string="Distribution",
        copy=True,
        help="Finished products obtained from the cutting layout, with how "
        "many of each come out of one unit of raw material.",
    )
    time_per_unit = fields.Float(
        string="Time per Unit",
        help="Estimated time, in minutes, to cut one unit of raw material. "
        "Used as the expected duration of the work order.",
    )
    planned_time = fields.Float(
        compute="_compute_planned_time",
        store=True,
        help="Time per Unit multiplied by the Quantity, in minutes.",
    )
    actual_time = fields.Float(
        compute="_compute_actual_time",
        store=True,
        readonly=False,
        help="Real duration, in minutes, of the work orders of every "
        "manufacturing order linked to this laser cutting order. Editable so "
        "an order recorded without a manufacturing order can still carry its "
        "real duration.",
    )
    consumed_material_weight = fields.Float(
        string="Consumed Material",
        compute="_compute_actual_amounts",
        store=True,
        help="Weight of raw material actually consumed across every linked "
        "manufacturing order.",
    )
    actual_output_material = fields.Float(
        compute="_compute_actual_amounts",
        store=True,
        help="Raw material attributable to the finished products actually "
        "produced across every linked manufacturing order: each produced "
        "quantity times the Consumption of its distribution line.",
    )
    actual_waste = fields.Float(
        compute="_compute_actual_amounts",
        store=True,
        help="Consumed Material minus Output Material: the raw material that "
        "did not end up in a finished product.",
    )
    planned_material_weight = fields.Float(
        string="Planned Material",
        compute="_compute_planned_waste",
        help="Quantity multiplied by Unit Weight: the raw material weight the "
        "order plans to consume.",
    )
    planned_output_material = fields.Float(
        compute="_compute_planned_waste",
        help="Quantity multiplied by the total Line consumption of the "
        "distribution: the raw material the finished products are expected to "
        "take.",
    )
    estimated_waste = fields.Float(
        compute="_compute_planned_waste",
        help="Planned Material minus Output Material. A negative value means "
        "the distribution lines claim more raw material than one unit "
        "provides, so the quantities need fixing.",
    )
    weight_uom_name = fields.Char(
        string="Weight Unit",
        compute="_compute_weight_uom_name",
        help="Unit of measure the weight figures of the order are expressed " "in.",
    )
    product_uom_name = fields.Char(
        related="bom_id.product_uom_id.name",
        string="Order Unit",
        help="Unit of measure of the Bill of Materials product, which the "
        "Quantity and Produced figures are expressed in.",
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
        readonly=True,
        copy=False,
        help="Initial manufacturing order generated from this laser cutting " "order.",
    )
    production_count = fields.Integer(
        string="Manufacturing Order Count",
        compute="_compute_production_count",
    )
    workorder_count = fields.Integer(
        string="Work Order Count",
        compute="_compute_workorder_count",
    )
    line_count = fields.Integer(
        string="Distribution Line Count",
        compute="_compute_line_count",
    )
    move_count = fields.Integer(
        string="Stock Move Count",
        compute="_compute_move_count",
        help="Stock moves that count as real consumption or output of the "
        "order: those of its manufacturing order chain plus any move linked "
        "straight to the order.",
    )

    def _get_productions(self):
        self.ensure_one()
        productions = self.production_id.procurement_group_id.mrp_production_ids
        return productions.filtered(
            lambda p: not p.laser_cut_order_id or p.laser_cut_order_id == self
        )

    def _get_consumed_material(self):
        self.ensure_one()
        return self.offcut_product_id if self.use_offcut else self.raw_material_id

    def _get_actual_moves(self):
        """Stock moves that count as real consumption/output of this order.

        The moves of the generated manufacturing order chain, plus any move
        linked straight to the order (``laser_cut_order_id``) for cuts
        recorded without a manufacturing order.
        """
        self.ensure_one()
        productions = self._get_productions()
        moves = productions.move_raw_ids | productions.move_finished_ids
        moves |= self.env["stock.move"].search([("laser_cut_order_id", "=", self.id)])
        return moves

    def _get_weight_uom(self):
        return self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()

    def _is_weight_uom(self, uom):
        return uom.category_id == self._get_weight_uom().category_id

    def _get_piece_uom(self):
        return self.env.ref("uom.product_uom_unit")

    def _uom_to_pieces(self, quantity, uom):
        piece_uom = self._get_piece_uom()
        if uom.category_id == piece_uom.category_id:
            return uom._compute_quantity(quantity, piece_uom)
        return quantity

    def _get_material_qty(self):
        self.ensure_one()
        material = self._get_consumed_material()
        if self._is_weight_uom(material.uom_id):
            return self._get_weight_uom()._compute_quantity(
                self.material_qty * self.material_unit_weight, material.uom_id
            )
        return self.material_qty

    def _get_line_qty(self, line):
        self.ensure_one()
        return self.material_qty * line.output_per_unit

    def _get_move_weight(self, move, unit_weight):
        self.ensure_one()
        if self._is_weight_uom(move.product_uom):
            return move.product_uom._compute_quantity(
                move.quantity, self._get_weight_uom()
            )
        return self._uom_to_pieces(move.quantity, move.product_uom) * unit_weight

    def _check_uom_categories(self):
        self.ensure_one()
        supported = (
            self._get_piece_uom().category_id | self._get_weight_uom().category_id
        )
        products = self._get_consumed_material() | self.line_ids.product_id
        wrong = products.filtered(lambda p: p.uom_id.category_id not in supported)
        if wrong:
            raise UserError(
                _(
                    "Laser cutting orders only handle products measured by "
                    "weight or in units. These are not: %s",
                    ", ".join(wrong.mapped("display_name")),
                )
            )

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
                order.state = "in_progress"
            elif "done" in states and "confirmed" in states:
                order.state = "in_progress"
            elif "done" in states:
                order.state = "done"
            elif "confirmed" in states:
                order.state = "confirmed"
            else:
                order.state = "cancelled"

    @api.depends(
        "production_id.product_qty",
        "production_id.procurement_group_id.mrp_production_ids.product_qty",
        "production_id.procurement_group_id.mrp_production_ids.state",
    )
    def _compute_material_qty(self):
        for order in self:
            productions = order._get_productions().filtered(
                lambda p: p.state != "cancel"
            )
            if productions:
                order.material_qty = sum(productions.mapped("product_qty"))

    @api.depends("raw_material_id.weight")
    def _compute_material_unit_weight(self):
        for order in self:
            if order.production_id:
                continue
            order.material_unit_weight = order.raw_material_id.weight

    @api.depends(
        "production_id.qty_produced",
        "production_id.procurement_group_id.mrp_production_ids.qty_produced",
    )
    def _compute_produced_qty(self):
        for order in self:
            order.produced_qty = sum(order._get_productions().mapped("qty_produced"))

    @api.depends("time_per_unit", "material_qty")
    def _compute_planned_time(self):
        for order in self:
            order.planned_time = order.time_per_unit * order.material_qty

    @api.depends(
        "production_id.workorder_ids.duration",
        "production_id.procurement_group_id.mrp_production_ids.workorder_ids.duration",
    )
    def _compute_actual_time(self):
        for order in self:
            productions = order._get_productions()
            order.actual_time = sum(productions.workorder_ids.mapped("duration"))

    def _compute_weight_uom_name(self):
        weight_uom_name = self._get_weight_uom().display_name
        for order in self:
            order.weight_uom_name = weight_uom_name

    @api.depends(
        "material_unit_weight",
        "line_ids.product_id",
        "line_ids.unit_consumption",
        "production_id.move_raw_ids.state",
        "production_id.move_raw_ids.quantity",
        "production_id.move_finished_ids.state",
        "production_id.move_finished_ids.quantity",
        "production_id.procurement_group_id.mrp_production_ids.move_raw_ids.state",
        "production_id.procurement_group_id.mrp_production_ids.move_raw_ids.quantity",
        "production_id.procurement_group_id.mrp_production_ids.move_finished_ids.state",
        "production_id.procurement_group_id.mrp_production_ids.move_finished_ids.quantity",
    )
    def _compute_actual_amounts(self):
        direct_by_order = defaultdict(lambda: self.env["stock.move"])
        if self.ids:
            for move in self.env["stock.move"].search(
                [("laser_cut_order_id", "in", self.ids)]
            ):
                direct_by_order[move.laser_cut_order_id.id] |= move
        for order in self:
            material = order._get_consumed_material()
            line_products = order.line_ids.product_id
            consumption_by_product = {
                line.product_id: line.unit_consumption for line in order.line_ids
            }
            productions = order._get_productions()
            moves = (
                productions.move_raw_ids
                | productions.move_finished_ids
                | direct_by_order.get(order.id, self.env["stock.move"])
            )
            done_moves = moves.filtered(lambda m: m.state == "done")
            raw_moves = done_moves.filtered(
                lambda m, material=material: m.product_id == material
            )
            output_moves = done_moves.filtered(
                lambda m, products=line_products: m.product_id in products
            )
            order.consumed_material_weight = sum(
                order._get_move_weight(move, order.material_unit_weight)
                for move in raw_moves
            )
            order.actual_output_material = sum(
                order._get_move_weight(
                    move,
                    consumption_by_product.get(move.product_id, move.product_id.weight),
                )
                for move in output_moves
            )
            order.actual_waste = (
                order.consumed_material_weight - order.actual_output_material
            )

    @api.depends("material_qty", "material_unit_weight", "line_ids.line_consumption")
    def _compute_planned_waste(self):
        for order in self:
            consumption_per_unit = sum(order.line_ids.mapped("line_consumption"))
            order.planned_material_weight = (
                order.material_qty * order.material_unit_weight
            )
            order.planned_output_material = order.material_qty * consumption_per_unit
            order.estimated_waste = (
                order.planned_material_weight - order.planned_output_material
            )

    @api.depends("production_id")
    def _compute_production_count(self):
        for order in self:
            order.production_count = len(order._get_productions())

    @api.depends("production_id")
    def _compute_workorder_count(self):
        for order in self:
            order.workorder_count = len(order._get_productions().workorder_ids)

    @api.depends("line_ids")
    def _compute_line_count(self):
        for order in self:
            order.line_count = len(order.line_ids)

    @api.depends("production_id")
    def _compute_move_count(self):
        for order in self:
            order.move_count = len(order._get_actual_moves())

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("mrp.laser.cut.order") or "New"
                )
        return super().create(vals_list)

    def unlink(self):
        if any(order.production_id for order in self):
            raise UserError(
                _(
                    "You cannot delete a laser cutting order that already has "
                    "a manufacturing order."
                )
            )
        return super().unlink()

    def _prepare_production_values(self):
        self.ensure_one()
        bom = self.bom_id
        product = bom.product_id or bom.product_tmpl_id.product_variant_id
        production_model = self.env["mrp.production"]
        picking_type = bom.picking_type_id or self.env["stock.picking.type"].browse(
            production_model._get_default_picking_type_id(self.env.company.id)
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
            "product_qty": self.material_qty,
            "origin": self.name,
            "laser_cut_order_id": self.id,
            "picking_type_id": picking_type.id,
            "location_src_id": location_src.id,
            "location_dest_id": location_dest.id,
        }

    def _prepare_consumption_move_values(self, production):
        self.ensure_one()
        material = self._get_consumed_material()
        return {
            "raw_material_production_id": production.id,
            "laser_cut_order_id": self.id,
            "product_id": material.id,
            "product_uom_qty": self._get_material_qty(),
            "product_uom": material.uom_id.id,
            "name": material.display_name,
        }

    def _prepare_byproduct_move_values(self, production, line):
        return {
            "production_id": production.id,
            "laser_cut_order_id": self.id,
            "laser_cut_order_line_id": line.id,
            "product_id": line.product_id.id,
            "product_uom_qty": self._get_line_qty(line),
            "product_uom": line.product_id.uom_id.id,
            "name": line.product_id.display_name,
        }

    def action_create_production(self):
        self.ensure_one()
        if self.production_id and self.production_id.state != "cancel":
            raise UserError(
                _("This laser cutting order already has a manufacturing order.")
            )
        if not self.line_ids:
            raise UserError(
                _(
                    "You need at least one distribution line to create a "
                    "manufacturing order."
                )
            )
        self._check_uom_categories()
        production = self.env["mrp.production"].create(
            self._prepare_production_values()
        )
        production.workorder_ids.write({"duration_expected": self.planned_time})
        production.action_confirm()
        moves = self.env["stock.move"].create(
            [self._prepare_consumption_move_values(production)]
            + [
                self._prepare_byproduct_move_values(production, line)
                for line in self.line_ids
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
                        "You cannot cancel a laser cutting order that already "
                        "has completed stock moves; cancel the manufacturing "
                        "order directly instead."
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

    def action_view_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_laser_cut.mrp_laser_cut_order_line_action"
        )
        action["domain"] = [("order_id", "=", self.id)]
        action["context"] = {"default_order_id": self.id}
        return action

    def action_view_moves(self):
        self.ensure_one()
        moves = self._get_actual_moves()
        return {
            "type": "ir.actions.act_window",
            "name": _("Stock Moves"),
            "res_model": "stock.move",
            "view_mode": "list,form",
            "domain": [("id", "in", moves.ids)],
            "context": {"create": False},
        }
