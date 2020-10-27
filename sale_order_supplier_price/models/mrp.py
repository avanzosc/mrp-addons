# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _
from odoo.addons import decimal_precision as dp


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    profit_percent = fields.Float(string="Profit percentage")
    commercial_percent = fields.Float(string="Commercial percentage")
    external_commercial_percent = fields.Float(
        string="External commercial percentage")
    profit_total = fields.Float(
        string="Profit Total", compute="_compute_commercial",
        digits=dp.get_precision("Product Price"))
    commercial_total = fields.Float(
        string="Commercial", compute="_compute_commercial",
        digits=dp.get_precision("Product Price"))
    external_commercial_total = fields.Float(
        string="External Commercial", compute="_compute_commercial",
        digits=dp.get_precision("Product Price"))
    production_total_unit = fields.Float(
        string="Total (by unit)", compute="_compute_production_total",
        digits=dp.get_precision("Product Price"))

    @api.onchange("profit_percent", "commercial_percent",
                  "external_commercial_percent")
    def onchange_percentages(self):
        for line in self.mapped("product_line_ids"):
            line._onchange_percents()

    def _check_confirmation_conditions(self):
        for production in self:
            if production.sale_line_id and production.sale_line_id.state != \
                    'done':
                exceptions.Warning(_('{} linked {} sale order is not '
                                     'confirmed').format(
                    production.name, production.sale_line_id.order_id.name))
        return True

    def button_confirm(self):
        if self._check_confirmation_conditions():
            super().button_confirm()

    @api.multi
    def action_confirm(self):
        res = super().action_confirm()
        self.mapped(
            "product_line_ids.sale_line_id").sudo().with_context(
            default_company_id=self.company_id.id,
            force_company=self.company_id.id
        )._timesheet_service_generation()
        return res

    @api.depends("product_line_ids", "product_line_ids.profit",
                 "product_line_ids.commercial",
                 "product_line_ids.external_commercial")
    def _compute_commercial(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        by_unit = get_param('mrp.subtotal_by_unit') == 'True'
        for prod in self:
            profit_total = sum(prod.mapped("product_line_ids.profit"))
            prod.profit_total = (
                profit_total / (prod.product_qty or 1.0) if by_unit else
                profit_total)
            commercial_total = sum(
                prod.mapped("product_line_ids.commercial"))
            prod.commercial_total = (
                commercial_total / (prod.product_qty or 1.0) if by_unit else
                commercial_total)
            external_total = sum(
                prod.mapped("product_line_ids.external_commercial"))
            prod.external_commercial_total = (
                external_total / (prod.product_qty or 1.0) if by_unit else
                external_total)

    @api.depends("product_qty", "scheduled_total", "profit_total",
                 "commercial_total", "external_commercial_total")
    def _compute_production_total(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        by_unit = get_param('mrp.subtotal_by_unit') == 'True'
        for prod in self:
            super(MrpProduction, prod)._compute_production_total()
            total = (
                prod.scheduled_total + prod.profit_total +
                prod.commercial_total + prod.external_commercial_total)
            prod.production_total = (
                total * (prod.product_qty if by_unit else 1))
            prod.production_total_unit = (
                total / (prod.product_qty or 1.0))

    @api.multi
    def _action_compute_lines(self):
        """ Compute product_lines from BoM structure
        @return: product_lines
        """
        results = super(MrpProduction, self)._action_compute_lines()
        self.mapped("product_line_ids")._onchange_percents()
        return results

    @api.multi
    def update_related_sale_line(self):
        for record in self.filtered("sale_line"):
            record.sale_line.write({
                "product_uom_qty": record.product_qty,
                "price_unit": record.production_total_unit,
            })

    @api.multi
    def button_recompute_total(self):
        fields_list = ["profit_total", "commercial_total",
                       "external_commercial_total", "production_total_unit"]
        for field in fields_list:
            self.env.add_todo(self._fields[field], self)
        super().button_recompute_total()
