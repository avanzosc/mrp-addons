# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    last_production_cost = fields.Float(
        string='Last Production Cost',
        compute='_compute_las_production_cost')
    production_cost_average = fields.Float(
        string='Production Cost Average')
    production_ids = fields.One2many(
        string='Production',
        comodel_name='mrp.production',
        inverse_name='product_tmpl_id')

    @api.depends("production_ids", "production_ids.state")
    def _compute_las_production_cost(self):
        self.last_production_cost = 0
        productions = self.production_ids.filtered(lambda p: p.state == "done")
        if productions:
            last_prduction = max(productions.mapped('id'))
            las_prduction = self.env['mrp.production'].search(
                [('id', '=', last_prduction)], limit=1)
            self.last_production_cost = las_prduction.cost_real_unit

    @api.multi
    def action_update_manufactured_product_price(self):
        self.ensure_one()
        productions = self.production_ids.filtered(lambda p: p.state == "done")
        if productions:
            n = len(productions)
            self.production_cost_average = sum(
                productions.mapped('cost_real_unit')) / n
            self.standard_price = self.production_cost_average
