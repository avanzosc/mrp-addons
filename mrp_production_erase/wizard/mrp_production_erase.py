# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, api


class MrpProductionErase(models.TransientModel):
    _name = 'mrp.production.erase'
    _description = 'Erase production'

    @api.multi
    def erase_productions(self):
        mrp_obj = self.env['mrp.production']
        for production_id in self.env.context['active_ids']:
            production = mrp_obj.browse(production_id)
            if production.state in ('progress', 'done'):
                continue
            production.action_cancel()
            if production.state == 'cancel':
                production.unlink()
        return {'type': 'ir.actions.act_window_close'}
