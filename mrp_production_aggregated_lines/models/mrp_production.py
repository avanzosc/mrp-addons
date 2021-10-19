# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_line_ids = fields.One2many(
        comodel_name="sale.order.line", inverse_name="mrp_production_id")
    stock_qty = fields.Float(string="Qty to Stock", readonly=True,
                             states={"draft": [("readonly", False)]})
    sale_line_qty = fields.Float(string="Sale qty",
                                 compute="_compute_sale_qty")
    # partner_ids = fields.Many2many(
    #     comodel_name="res.partner",
    #     relation="mrp_production_res_partner_rel",
    #     column1="mrp_production_id",
    #     column2="res_partner_id",
    #     string="Customer", store=True,
    #     compute="_compute_partner_id")
    #
    # @api.depends("sale_line_ids")
    # def _compute_partner_id(self):
    #     for production in self:
    #         production.partner_ids = [(6, 0, production.sale_line_ids.mapped(
    #             "order_id.partner_id").ids)]

    @api.depends("sale_line_ids")
    def _compute_sale_qty(self):
        for production in self:
            production.sale_line_qty = sum(production.sale_line_ids.mapped(
                "product_uom_qty"))

    @api.onchange("stock_qty", "sale_line_qty")
    def _onchange_stock_qty(self):
        for production in self:
            production.product_qty = (production.stock_qty +
                                      production.sale_line_qty)

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        for production in self:
            production.stock_qty = (production.product_qty -
                                    production.sale_line_qty)

    def _update_mo_qty(self, qty):
        self.ensure_one()
        self.product_qty = qty
        self.action_compute()

    def action_cancel(self):
        res = super().action_cancel()
        for production in self:
            if production.sale_line_ids:
                production.sale_line_ids.write(
                    {"mrp_production_id": False})
                production.write({"sale_line_ids": [[5]]})
        return res

    def _recalculate_origin(self):
        self.ensure_one()
        return ", ".join(self.mapped("sale_line_ids.order_id.name"))

    def _recalculate_mo_qty(self):
        self.ensure_one()
        return sum(self.sale_line_ids.mapped(
            "product_uom_qty")) + self.stock_qty

    @api.onchange("stock_qty", "sale_line_ids")
    def _action_recalculate_product_qty(self):
        for mrp in self:
            mrp.product_qty = mrp._recalculate_mo_qty()

    @api.onchange("product_qty")
    def _action_recalculate_lines(self):
        for production in self:
            res = production._prepare_lines()
            results = res  # product_lines
            prod_lines = []
            for line in results:
                line_data = line[1]
                bom_line = line[0]
                product = bom_line.product_id
                prod_line = {
                    "name": product.name or bom_line.product_tmpl_id.name,
                    "product_id": product.id,
                    "product_qty": line_data["qty"],
                    "bom_line_id": bom_line.id,
                    "product_uom_id": bom_line.product_uom_id.id,
                    "production_id": production.id,
                }
                prod_lines.append(prod_line)
            production.update({
                "product_line_ids": [
                    (2, line.id) for line in production.product_line_ids],
            })
            production.update({
                "product_line_ids": prod_lines,
            })
