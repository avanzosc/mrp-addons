# Copyright 2026 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from collections import defaultdict

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    laser_material_id = fields.Many2one(
        related="product_id.laser_material_id", store=True, readonly=True
    )
    material_unit_weight = fields.Float(
        related="laser_material_id.weight",
        string="Material Unit Weight",
        readonly=True,
    )
    product_unit_weight = fields.Float(
        related="product_id.weight", string="Product Unit Weight", readonly=True
    )

    def action_open_laser_orderpoints(self):
        self._get_orderpoint_action()
        return self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_laser_cut.action_stock_warehouse_orderpoint_laser"
        )

    def action_create_laser_order(self):
        if not self:
            raise UserError(_("Select at least one line."))
        if any(not orderpoint.laser_material_id for orderpoint in self):
            raise UserError(_("All the selected lines must have a laser material."))
        line_obj = self.env["order.olaser.lista"]
        groups = defaultdict(lambda: self.env[self._name])
        for orderpoint in self:
            groups[orderpoint.laser_material_id] += orderpoint
        orders = self.env["order.olaser"]
        for material, orderpoints in groups.items():
            orders |= self.env["order.olaser"].create(
                {
                    "product_id": material.id,
                    "peso_mp": material.weight,
                    "cantidad": 1,
                    "listas_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": orderpoint.product_id.id,
                                "cantidad_chapa": orderpoint.qty_to_order,
                                "cantidad_consumo": line_obj._get_bom_qty(
                                    orderpoint.product_id, material
                                ),
                            },
                        )
                        for orderpoint in orderpoints
                    ],
                }
            )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp_laser_cut.action_order_olaser"
        )
        if len(orders) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = orders.id
        else:
            action["domain"] = [("id", "in", orders.ids)]
        return action
