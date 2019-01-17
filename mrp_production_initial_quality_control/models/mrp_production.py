# -*- coding: utf-8 -*-
# Copyright 2019 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api
from openerp.addons.quality_control.models.qc_trigger_line import\
    _filter_trigger_lines


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_confirm(self):
        inspection_obj = self.env['qc.inspection']
        result = super(MrpProduction, self).action_confirm()
        for production in self:
            for move in production.move_created_ids.filtered(
                    lambda r: r.state not in ('done', 'cancel')):
                qc_trigger = self.env.ref(
                    'mrp_production_initial_quality_control.qc_trigger_mrp_i')
                trigger_lines = set()
                for model in ['qc.trigger.product_category_line',
                              'qc.trigger.product_template_line',
                              'qc.trigger.product_line']:
                    trigger_lines = trigger_lines.union(
                        self.env[model].get_trigger_line_for_product(
                            qc_trigger, move.product_id))
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspection_obj._make_inspection(move, trigger_line)
        return result
