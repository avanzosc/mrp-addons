# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests import common


class MrpWorkorderGroupingMaterial(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        product_obj = cls.env["product.product"]
        bom_obj = cls.env["mrp.bom"]
        operation_model = cls.env["mrp.routing.workcenter"]
        workcenter_model = cls.env["mrp.workcenter"]
        production_model = cls.env["mrp.production"]
        unit_id = cls.env.ref("uom.product_uom_unit")
        cls.man_product = product_obj.create(
            {
                "name": "Manufacturing Product",
                "uom_id": unit_id.id,
                "route_ids": [
                    (4, manufacture_route.id),
                    (4, mto_route.id),
                ],
            }
        )
        cls.workcenter = workcenter_model.create(
            {
                "name": "wc1",
            }
        )
        cls.workcenter2 = workcenter_model.create(
            {
                "name": "wc2",
                "nesting_required": True,
            }
        )
        cls.operation1 = operation_model.create(
            {
                "name": "op1",
                "workcenter_id": cls.workcenter.id,
            }
        )
        cls.operation2 = operation_model.create(
            {
                "name": "op2",
                "workcenter_id": cls.workcenter2.id,
            }
        )
        cls.component = product_obj.create(
            {
                "name": "Component",
            }
        )
        cls.main_component = product_obj.create(
            {
                "name": "Main Component",
            }
        )
        cls.bom = bom_obj.create(
            {
                "product_tmpl_id": cls.man_product.product_tmpl_id.id,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.component.id,
                            "product_qty": 2.0,
                            "operation_id": cls.operation1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.main_component.id,
                            "product_qty": 3.0,
                            "operation_id": cls.operation2.id,
                            "main_material": True,
                        },
                    ),
                ],
            }
        )
        today = fields.Datetime.now()
        cls.production_id = production_model.create(
            {
                "product_id": cls.man_product.id,
                "product_qty": 4,
                "product_uom_id": unit_id.id,
                "bom_id": cls.bom.id,
                "date_planned_start": today,
            }
        )
        cls.production_id.onchange_product_id()
        cls.production_id._onchange_bom_id()
        cls.production_id._onchange_move_raw()
