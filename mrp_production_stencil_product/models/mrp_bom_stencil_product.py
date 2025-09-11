# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBomStencilProduct(models.Model):
    _name = "mrp.bom.stencil.product"
    _description = "Stentil products in BoMs"
    _rec_name = "product_id"

    bom_id = fields.Many2one(
        string="BoM",
        comodel_name="mrp.bom",
        copy=False,
        required=True,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        copy=False,
    )
    location_id = fields.Many2one(
        string="Location",
        comodel_name="stock.location",
        copy=False,
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
        copy=False,
        default=1.0,
    )
    product_uom_id = fields.Many2one(
        string="Unit of measure",
        comodel_name="uom.uom",
        copy=False,
    )
