from odoo import fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        related="workorder_id.product_id",
        store=True,
        readonly=True,
    )
    production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        related="workorder_id.production_id",
        store=True,
        readonly=True,
    )
    procurement_group_id = fields.Many2one(
        "procurement.group",
        string="Procurement Group",
        related="workorder_id.production_id.procurement_group_id",
        store=True,
        readonly=True,
    )
