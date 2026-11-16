# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections import defaultdict
from math import ceil

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    laser_material_id = fields.Many2one(
        comodel_name="product.product",
        related="product_id.laser_material_id",
        string="Raw Material",
        store=True,
        readonly=True,
        help="Raw material the product is cut from, taken from its laser "
        "cutting Bill of Materials. Products replenished from the same raw "
        "material are grouped into one laser cutting order.",
    )
    material_unit_weight = fields.Float(
        related="laser_material_id.weight",
        string="Unit Weight",
        store=True,
        readonly=True,
        aggregator="min",
        help="Weight of one unit of the raw material this product is cut "
        "from, taken from the raw material product itself.",
    )
    unit_consumption = fields.Float(
        string="Consumption",
        compute="_compute_unit_consumption",
        digits="Stock Weight",
        help="Weight of raw material one unit of this product consumes, "
        "according to the Bill of Materials that cuts it from that material, "
        "or the weight of the product when that Bill of Materials does not "
        "give it.",
    )

    @api.depends("product_id", "laser_material_id")
    def _compute_unit_consumption(self):
        line_model = self.env["mrp.laser.cut.order.line"]
        for orderpoint in self:
            orderpoint.unit_consumption = (
                line_model._get_unit_consumption(
                    orderpoint.product_id, orderpoint.laser_material_id
                )
                or orderpoint.product_id.weight
            )

    def _get_replenishment_qty(self):
        self.ensure_one()
        return self.qty_to_order

    @api.model
    def _web_read_group(
        self,
        domain,
        fields,
        groupby,
        limit=None,
        offset=0,
        orderby=False,
        lazy=True,
    ):
        groups = super()._web_read_group(
            domain,
            fields,
            groupby,
            limit=limit,
            offset=offset,
            orderby=orderby,
            lazy=lazy,
        )
        if not self.env.context.get("laser_replenishment"):
            return groups
        for group in groups:
            orderpoints = self.search(group.get("__domain") or domain)
            group["qty_to_order"] = sum(orderpoints.mapped("qty_to_order"))
            group["unit_consumption"] = sum(orderpoints.mapped("unit_consumption"))
        return groups

    def action_open_laser_orderpoints(self):
        self._get_orderpoint_action()
        return self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_laser_cut.stock_warehouse_orderpoint_laser_action"
        )

    @api.model
    def _best_laser_fill(self, capacity, sizes, max_nodes=200000):
        indexes = sorted(
            (i for i, size in enumerate(sizes) if size > 0),
            key=lambda i: -sizes[i],
        )
        counts = [0] * len(sizes)
        best = {"key": (0, 0), "counts": list(counts)}
        nodes = [0]

        def explore(pos, left, pieces):
            nodes[0] += 1
            index = indexes[pos]
            if pos == len(indexes) - 1:
                qty = left // sizes[index]
                counts[index] = qty
                key = (capacity - left + qty * sizes[index], pieces + qty)
                if key > best["key"]:
                    best["key"] = key
                    best["counts"] = list(counts)
                counts[index] = 0
                return
            smallest = min(sizes[i] for i in indexes[pos:])
            for qty in range(left // sizes[index], -1, -1):
                rest = left - qty * sizes[index]
                if best["key"][0] == capacity and (
                    pieces + qty + rest // smallest <= best["key"][1]
                ):
                    continue
                counts[index] = qty
                explore(pos + 1, rest, pieces + qty)
                if nodes[0] >= max_nodes:
                    break
            counts[index] = 0

        if indexes and capacity > 0:
            explore(0, capacity, 0)
        return best["counts"]

    def _seed_laser_layout(self, material):
        digits = self.env["decimal.precision"].precision_get("Stock Weight")
        scale = 10**digits
        unit_weight = material.weight
        if float_compare(unit_weight, 0, precision_digits=digits) <= 0:
            raise UserError(
                _(
                    "Set the weight of the raw material %s before creating a "
                    "laser cutting order from replenishment.",
                    material.display_name,
                )
            )
        capacity = int(float_round(unit_weight * scale, 0, rounding_method="DOWN"))
        demand = {
            op: max(
                0,
                ceil(
                    float_round(
                        op._get_replenishment_qty(),
                        precision_rounding=op.product_uom.rounding,
                    )
                ),
            )
            for op in self
        }
        needed = self.filtered(lambda op: demand[op] > 0)
        if not needed:
            raise UserError(
                _(
                    "There is nothing to replenish from the raw material %s.",
                    material.display_name,
                )
            )
        size = {
            op: int(float_round(op.unit_consumption * scale, 0, rounding_method="UP"))
            for op in self
        }
        missing = needed.filtered(lambda op: size[op] <= 0)
        if missing:
            raise UserError(
                _(
                    "Set the consumption (Bill of Materials or product weight) "
                    "of these products: %s",
                    ", ".join(missing.product_id.mapped("display_name")),
                )
            )
        if sum(size[op] for op in needed) > capacity:
            raise UserError(
                _(
                    "One unit of %(material)s (%(weight)s) cannot hold one "
                    "piece of each of these products at once: %(products)s. "
                    "Create separate laser cutting orders for them.",
                    material=material.display_name,
                    weight=unit_weight,
                    products=", ".join(needed.product_id.mapped("display_name")),
                )
            )

        def outputs_for(qty):
            return {op: ceil(demand[op] / qty) for op in self}

        def used_by(outputs):
            return sum(size[op] * outputs[op] for op in self)

        demand_size = sum(size[op] * demand[op] for op in self)
        material_qty = max(1, ceil(demand_size / capacity))
        outputs = outputs_for(material_qty)
        while used_by(outputs) > capacity:
            material_qty += 1
            outputs = outputs_for(material_qty)
        extra = self._best_laser_fill(
            capacity - used_by(outputs), [size[op] for op in needed]
        )
        for op, qty in zip(needed, extra, strict=True):
            outputs[op] += qty
        return material_qty, outputs

    def action_create_laser_order(self):
        if not self:
            raise UserError(_("Select at least one line."))
        if any(not orderpoint.laser_material_id for orderpoint in self):
            raise UserError(_("Every selected line must have a raw material."))
        groups = defaultdict(lambda: self.env[self._name])
        for orderpoint in self:
            groups[orderpoint.laser_material_id] += orderpoint
        orders = self.env["mrp.laser.cut.order"]
        for material, orderpoints in groups.items():
            material_qty, outputs = orderpoints._seed_laser_layout(material)
            order = self.env["mrp.laser.cut.order"].create(
                {
                    "raw_material_id": material.id,
                    "material_unit_weight": material.weight,
                    "material_qty": material_qty,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": orderpoint.product_id.id,
                                "output_per_unit": outputs[orderpoint],
                            },
                        )
                        for orderpoint in orderpoints
                    ],
                }
            )
            orders |= order
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_laser_cut.mrp_laser_cut_order_action"
        )
        if len(orders) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = orders.id
        else:
            action["domain"] = [("id", "in", orders.ids)]
        return action
