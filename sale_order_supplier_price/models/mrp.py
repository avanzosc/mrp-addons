# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    profit_percent = fields.Float(string='Profit percentage')
    commercial_percent = fields.Float(string='Commercial percentage')
    # currency_id = fields.Many2one(
    #     comodel_name='res.currency', string='Currency',
    #     related='company_id.currency_id')
    commercial_percent = fields.Float(string='Commercial percentage')
    external_commercial_percent = fields.Float(
        string='External commercial percentage')
    profit_percent_update = fields.Boolean(string='Update profit')
    commercial_percent_update = fields.Boolean(string='Commercial profit')
    external_percent_update = fields.Boolean(string='External profit')
    scheduled_profit = fields.Float(
        string='Profit', compute='_compute_scheduled_total',
        digits=dp.get_precision('Product Price'))
    scheduled_commercial = fields.Float(
        string='Commercial', compute='_compute_scheduled_total',
        digits=dp.get_precision('Product Price'))
    scheduled_cost_total = fields.Float(
        string='Scheduled Total', compute='_compute_scheduled_total',
        digits=dp.get_precision('Product Price'))
    commercial_total = fields.Float(
        string='Commercial', compute='_compute_commercial',
        digits=dp.get_precision('Product Price'))
    external_commercial_total = fields.Float(
        string='External Commercial', compute='_compute_commercial',
        digits=dp.get_precision('Product Price'))
    external_total = fields.Float(
        string='External Total', compute='_compute_commercial',
        digits=dp.get_precision('Product Price'))
    production_total_unit = fields.Float(
        string='Total (by unit)', compute="_compute_production_total",
        digits=dp.get_precision('Product Price'))

    @api.multi
    def action_confirm(self):
        res = super().action_confirm()
        self.mapped('product_line_ids.sale_line_id').sudo().with_context(
                default_company_id=self.company_id.id,
                force_company=self.company_id.id,
            )._timesheet_service_generation()
        return res

    @api.depends('profit_percent', 'commercial_percent',
                 'product_line_ids', 'product_line_ids.subtotal')
    def _compute_scheduled_total(self):
        for prod in self.filtered(lambda m: m.product_line_ids and
                                  m.product_qty):
            super(MrpProduction, prod)._compute_scheduled_total()
            prod.scheduled_profit =\
                prod.scheduled_total * (prod.profit_percent / 100)
            prod.scheduled_cost_total =\
                prod.scheduled_total * ((100 + prod.profit_percent) / 100)
            prod.scheduled_commercial =\
                prod.scheduled_cost_total * (prod.commercial_percent / 100)

    @api.depends('production_total', 'commercial_percent',
                 'external_commercial_percent')
    def _compute_commercial(self):
        for prod in self:
            prod.commercial_total =\
                prod.production_total * (prod.commercial_percent / 100)
            prod.external_commercial_total = prod.production_total *\
                (prod.external_commercial_percent / 100)
            prod.external_total = prod.production_total *\
                ((100 + prod.external_commercial_percent) / 100)

    @api.depends('product_qty', 'scheduled_cost_total')
    def _compute_production_total(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        by_unit = get_param('mrp.subtotal_by_unit')
        for prod in self:
            super(MrpProduction, prod)._compute_production_total()
            total = prod.scheduled_cost_total
            prod.production_total =\
                total * (prod.product_qty if by_unit else 1)
            prod.production_total_unit =\
                prod.production_total / (prod.product_qty or 1.0)

    @api.multi
    def update_related_sale_line(self):
        for record in self.filtered('sale_line'):
            record.sale_line.write({
                'product_uom_qty': record.product_qty,
                'price_unit': record.production_total_unit,
            })

    def button_recompute_total(self):
        for line in self.product_line_ids:
            if self.profit_percent_update:
                line.profit = \
                    line.subtotal * (line.production_id.profit_percent / 100)
            if self.commerctial_percent_update:
                line.commercial = \
                    (line.subtotal + line.profit) * \
                    (line.production_id.commercial_percent / 100)
            if self.external_percent_update:
                line.external_commercial = \
                    (line.subtotal + line.profit) * \
                    (line.production_id.external_commercial_percent / 100)
        return super().button_recompute_total()


class MrpProductionProductLine(models.Model):
    _inherit = "mrp.production.product.line"

    sale_line_id = fields.Many2one(comodel_name="sale.order.line",
                                   string="Sale line",
                                   related="production_id.sale_line_id",
                                   store=True)
    order_id = fields.Many2one(comodel_name="sale.order",
                               related="sale_line_id.order_id", store=True)
    # bom_products = fields.Many2many(comodel_name="product.product",
    #                                 compute="_compute_bom_products")
    profit = fields.Float(
        string='Profit',
        digits=dp.get_precision('Product Price'),
        )
    commercial = fields.Float(
        string='Commercial',
        digits=dp.get_precision('Product Price'),
        )
    external_commercial = fields.Float(
        string='External',
        digits=dp.get_precision('Product Price'),
        )
    price = fields.Float(
        string='Price', compute='_compute_profit',
        digits=dp.get_precision('Product Price'),
        store=True)
    categ_id = fields.Many2one(comodel_name="product.category",
                                   related="product_id.categ_id",
                                   string="Category", store=True)
    service_type = fields.Many2one(comodel_name="service.type",
                                   related="product_id.categ_id.service_type",
                                   string="Service Type", store=True)

    # @api.depends('sale_line_id')
    # def _compute_bom_products(self):
    #     for line in self:
    #         if line.sale_line_id:
    #             product = line.sale_line_id.product_id

    @api.onchange('subtotal')
    def _onchange_percents(self):
        for mrp in self:
            mrp.profit = \
                mrp.subtotal * (mrp.production_id.profit_percent / 100)
            mrp.commercial = \
                (mrp.subtotal + mrp.profit) * \
                (mrp.production_id.commercial_percent / 100)
            mrp.external_commercial = \
                (mrp.subtotal + mrp.profit) * \
                (mrp.production_id.external_commercial_percent / 100)

    @api.depends('profit', 'subtotal', 'commercial', 'external_commercial')
    def _compute_profit(self):
        for mrp in self:
            mrp.price = mrp.subtotal + mrp.profit + mrp.commercial + \
                        mrp.external_commercial
