# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    subtotal_by_unit = fields.Boolean(
        string='Compute unitary total values',
        help='This will allow you to define if the total of the scheduled '
        'product list is computed by unit or not.')
    group_show_unitary_info = fields.Boolean(
        string="Show Unitary Info in Scheduled Lines",
        implied_group="mrp_supplier_price.group_show_unitary_info")

    @api.model
    def get_values(self):
        res = super(MrpConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        # the value of the parameter is a nonempty string
        res.update(
            subtotal_by_unit=get_param('mrp.subtotal_by_unit',
                                       'False').lower() == 'true',
        )
        return res

    @api.multi
    def set_values(self):
        super(MrpConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        # we store the repr of the values, since the value of the parameter is
        # a required string
        set_param('mrp.subtotal_by_unit', repr(self.subtotal_by_unit))
