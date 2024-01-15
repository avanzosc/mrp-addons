# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    semi_finished = fields.Boolean(
        string="Is semi-finished?", related="product_id.semi_finished")
    qty_available = fields.Float(
        string="Quantity On Hand", related="product_id.qty_available",
        digits="Product Unit of Measure")
    virtual_available = fields.Float(
        string="Forecast Quantity", related="product_id.virtual_available",
        digits="Product Unit of Measure")
    product_to_produce_id = fields.Many2one(
        string="Product to produce", comodel_name="product.product",
        related="bom_id.product_id", store=True, copy=False)
    bom_code = fields.Char(
        string="BoM Reference", related="bom_id.code", store=True,
        copy=False)
    bom_type = fields.Selection(
        string="BoM Type", related="bom_id.type", store=True,
        copy=False)
