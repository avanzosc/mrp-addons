# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_line_id = fields.Many2one(
        string="Sale line", comodel_name="sale.order.line",
        copy=False)
    sale_id = fields.Many2one(
        string="Sale order", comodel_name="sale.order",
        related="sale_line_id.order_id", store=True, copy=False)
    sale_line_name = fields.Text(
        string="Sale line description", related="sale_line_id.name",
        store=True, copy=False)

    @api.model
    def create(self, values):
        if ("sale_line_id" in self.env.context and
                self.env.context.get("sale_line_id", False)):
            values["sale_line_id"] = self.env.context.get("sale_line_id")
        production = super(MrpProduction, self).create(values)
        if production.sale_line_id:
            production.sale_line_id.mrp_production_id = production.id
        return production
