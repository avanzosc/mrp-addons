# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models

PARAMS = [
    ("do_all", "mrp_workorder_moves_view.do_all"),
]

class ResConfingSettings(models.TransientModel):
    _inherit = "res.config.settings"

    do_all = fields.boolean(string="Process whole workorder")

    @api.multi
    def set_params(self):
        self.ensure_one()
        field_name = "mrp_workorder_moves_view.do_all"
        key_name = "do_all"
        value = getattr(self, field_name, '').strip()
        self.env['ir.config_parameter'].set_param(key_name, value)

    @api.multi
    def get_default_params(self, cr, uid, fields, context=None):
        res = {}
        for field_name, key_name in PARAMS:
            res[field_name] = self.env['ir.config_parameter'].get_param(
                key_name, '').strip()
        return res