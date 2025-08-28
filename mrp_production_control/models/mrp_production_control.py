# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductionControl(models.Model):
    _name = "mrp.production.control"
    _description = "Production Control"

    create_date = fields.Datetime(string="Date/Time", readonly=True)
    operator_id = fields.Many2one(
        comodel_name="res.users",
        string="Operator",
        default=lambda self: self.env.uid,
    )
    pallet_number = fields.Integer()
    controlled_pieces = fields.Integer()
    defective_pieces = fields.Integer()
    defect_description = fields.Char(size=200)
    action_taken = fields.Char(size=200)
    manufacturing_order_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
    )
    workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Work Order",
    )
    manufacturing_order_product_id = fields.Many2one(
        string="Product to produce",
        comodel_name="product.product",
        related="manufacturing_order_id.product_id",
        store=True,
        copy=False,
    )
    manufacturing_order_product_lot_id = fields.Many2one(
        string="Lot of product to produce",
        comodel_name="stock.lot",
        related="manufacturing_order_id.lot_producing_id",
        store=True,
        copy=False,
    )
    manual_date = fields.Datetime()

    @api.onchange("manufacturing_order_id")
    def _onchange_manufacturing_order_id(self):
        if (
            self.workorder_id
            and self.workorder_id.production_id != self.manufacturing_order_id
        ):
            self.workorder_id = False

    @api.onchange("workorder_id")
    def _onchange_workorder_id(self):
        if self.workorder_id:
            self.manufacturing_order_id = self.workorder_id.production_id

    @api.model_create_multi
    def create(self, vals_list):
        workorder_obj = self.env["mrp.workorder"]
        for vals in vals_list:
            if vals.get("workorder_id") and not vals.get("manufacturing_order_id"):
                workorder = workorder_obj.browse(vals["workorder_id"])
                vals["manufacturing_order_id"] = workorder.production_id.id
            vals["manual_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if (
                rec.workorder_id
                and rec.manufacturing_order_id != rec.workorder_id.production_id
            ):
                rec.manufacturing_order_id = rec.workorder_id.production_id
        return res
