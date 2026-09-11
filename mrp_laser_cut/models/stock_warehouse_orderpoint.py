# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections import defaultdict
from math import ceil

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
        help="Raw material one unit of this product consumes, in the unit of "
        "measure of the raw material, according to the Bill of Materials that "
        "cuts it from that material.",
    )

    @api.depends("product_id", "laser_material_id")
    def _compute_unit_consumption(self):
        line_model = self.env["mrp.laser.cut.order.line"]
        for orderpoint in self:
            orderpoint.unit_consumption = line_model._get_unit_consumption(
                orderpoint.product_id, orderpoint.laser_material_id
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

    def _seed_laser_layout(self, material):
        unit_weight = material.weight
        demand = {op: op._get_replenishment_qty() for op in self}
        demand_weight = sum(demand[op] * op.unit_consumption for op in self)
        if unit_weight <= 0 or demand_weight <= 0:
            return 1, demand
        material_qty = max(1, ceil(demand_weight / unit_weight))
        top_demand = max([1] + [q for q in demand.values() if q > 0])

        def outputs_for(qty):
            return {op: ceil(demand[op] / qty) if demand[op] > 0 else 0 for op in self}

        while material_qty < top_demand:
            outputs = outputs_for(material_qty)
            used = sum(op.unit_consumption * outputs[op] for op in self)
            if used <= unit_weight:
                return material_qty, outputs
            material_qty += 1
        return material_qty, outputs_for(material_qty)

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
