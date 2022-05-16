# Copyright 2021 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    long_cut = fields.Float(
        string="Long Cut (mm)",
        default=lambda self: self.bom_line_id.long_cut,
    )
    qty_pieces_set = fields.Integer(
        string="Quantity of Pieces in Set",
        default=lambda self: self.bom_line_id.qty_pieces_set,
    )
    waste_rate = fields.Float(
        string="Waste Rate",
        default=1.08,
    )
    qty_pieces_cut = fields.Float(
        string="Pieces to Cut",
        default=lambda self: self.qty_pieces_set,
    )
    second_uom_id = fields.Many2one(
        string="Second UOM",
        comodel_name="uom.uom",
        related="product_id.second_uom_id",
        store=True,
    )
    read_only = fields.Boolean(
        string="Read Only",
        compute="_compute_read_only",
    )

    @api.onchange("long_cut")
    def onchange_waste_rate(self):
        if self.long_cut <= 1000:
            self.waste_rate = 1.08
        elif self.long_cut > 1000 and self.long_cut <= 2300:
            self.waste_rate = 1.12
        elif self.long_cut > 2300 and self.long_cut <= 3000:
            self.waste_rate = 1.15
        else:
            self.waste_rate = 1.2

    @api.depends(
        "product_id", "product_uom", "second_uom_id", "product_id.dimensional_uom_id")
    def _compute_read_only(self):
        for line in self:
            read_only = False
            dim_uom = line.product_id.dimensional_uom_id
            if dim_uom != line.product_uom and dim_uom != line.second_uom_id:
                read_only = True
            line.read_only = read_only

    @api.onchange("long_cut", "qty_pieces_set", "waste_rate")
    def onchange_product_uom_qty(self):
        dim_uom = self.product_id.dimensional_uom_id
        if dim_uom == self.product_uom:
            self.product_uom_qty = (
                self.long_cut / 1000 * self.qty_pieces_set * self.waste_rate)
        elif dim_uom == self.second_uom_id:
            self.product_uom_qty = (
                self.long_cut / 1000 * self.qty_pieces_set *
                self.waste_rate * self.product_id.factor_inverse)

    @api.constrains("long_cut")
    def _check_check_long(self):
        if any(line.long_cut < 0.0 for line in self):
            raise UserError(_("The long cut must be strictly positive."))

    @api.constrains("long_cut", "product_id", "product_id.product_length")
    def _check_long_cut_length(self):
        for line in self.filtered(lambda l: l.long_cut and l.product_id.product_lenght):
            if line.long_cut / 1000 > line.product_id.product_length:
                raise ValidationError(
                    _("The long cut can't be longer than the length of the product"))
