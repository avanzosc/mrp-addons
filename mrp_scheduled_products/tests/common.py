# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class MrpProductionCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(MrpProductionCommon, cls).setUpClass()
        cls.mrp_production_model = cls.env["mrp.production"]
        cls.bom_model = cls.env["mrp.bom"]
        cls.product_model = cls.env["product.product"]
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy", False)
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture", False)
        unit = cls.env.ref("uom.product_uom_unit")
        dozen = cls.env.ref("uom.product_uom_dozen")
        cls.supplier = cls.env["res.partner"].create({
            "name": "Component Supplier"
        })
        cls.manufacture_product = cls.product_model.create({
            "name": "BoM product",
            "uom_id": unit.id,
            "route_ids": [(4, cls.manufacture_route.id)],
        })
        cls.buy_component = cls.product_model.create({
            "name": "Purchase Component",
            "standard_price": 10.0,
            "uom_id": dozen.id,
            "uom_po_id": unit.id,
            "route_ids": [
                (4, cls.buy_route.id),
            ],
            "seller_ids": [(0, 0, {
                "name": cls.supplier.id
            })]
        })
        cls.manufacture_component = cls.product_model.create({
            "name": "Manufacture Component",
            "standard_price": 15.0,
            "uom_id": unit.id,
            "uom_po_id": unit.id,
            "route_ids": [
                (4, cls.manufacture_route.id),
            ],
        })
        cls.mrp_bom = cls.bom_model.create({
            "product_tmpl_id": cls.manufacture_product.product_tmpl_id.id,
            "product_id": cls.manufacture_product.id,
            "bom_line_ids":
                [(0, 0, {
                    "product_id": cls.buy_component.id,
                    "product_qty": 2.0,
                }),
                 (0, 0, {
                     "product_id": cls.manufacture_component.id,
                     "product_qty": 12.0,
                 })],
        })
        cls.bom_model.create({
            "product_tmpl_id": cls.manufacture_component.product_tmpl_id.id,
            "product_id": cls.manufacture_component.id,
        })
        cls.production = cls.mrp_production_model.create({
            "product_id": cls.manufacture_product.id,
            "product_uom_id": cls.manufacture_product.uom_id.id,
        })
