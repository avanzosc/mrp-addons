# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductionControl(models.Model):
    _name = "mrp.production.control"

    create_date = fields.Datetime(string="Date/Time", readonly=True)
    operator_id = fields.Many2one(
        "res.users", string="Operator", default=lambda self: self.env.uid
    )
    pallet_number = fields.Integer()
    controlled_pieces = fields.Integer()
    defective_pieces = fields.Integer()
    defect_description = fields.Char(size=200)
    action_taken = fields.Char(size=200)
    manufacturing_order_id = fields.Many2one(
        "mrp.production", string="Manufacturing Order", domain=[]
    )
    workorder_id = fields.Many2one("mrp.workorder", string="Work Order", domain=[])

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

    @api.model
    def create(self, vals):
        if vals.get("workorder_id"):
            workorder = self.env["mrp.workorder"].browse(vals["workorder_id"])
            vals["manufacturing_order_id"] = workorder.production_id.id
        return super().create(vals)

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if (
                rec.workorder_id
                and rec.manufacturing_order_id != rec.workorder_id.production_id
            ):
                rec.manufacturing_order_id = rec.workorder_id.production_id
        return res
