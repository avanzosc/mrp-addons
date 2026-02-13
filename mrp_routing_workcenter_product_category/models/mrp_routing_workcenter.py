from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    categ_id = fields.Many2one(
        "product.category",
        related="bom_id.product_tmpl_id.categ_id",
        store=True,
        string="product category",
    )
