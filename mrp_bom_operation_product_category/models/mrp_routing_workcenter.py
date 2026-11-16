# Copyright 2026 Ane Gurruchaga - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    product_categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        related="bom_id.product_tmpl_id.categ_id",
        store=True,
        index=True,
    )
