# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    cost_real_unit = fields.Float(
        string='Cost Real Unit',
        compute='_compute_cost_real_unit',
        store=True)

    @api.depends("move_raw_ids.real_subcost")
    def _compute_cost_real_unit(self):
        for record in self:
            record.cost_real_unit = 0
            if record.product_qty != 0:
                record.cost_real_unit = sum(
                    record.move_raw_ids.mapped('real_subcost'))/(
                        record.product_qty)

    @api.multi
    def write(self, values):
        result = super(MrpProduction, self).write(values)
        if "state" in values and values['state'] == 'done':
            self.product_id.production_cost_average = (
                (self.product_id.qty_available - self.product_qty) * (
                    self.product_id.standard_price) + (
                        sum(self.move_raw_ids.mapped('real_subcost')))) / (
                            self.product_id.qty_available)
            self.product_id.standard_price = (
                self.product_id.production_cost_average)
        return result
