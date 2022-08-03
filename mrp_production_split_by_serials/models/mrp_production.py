# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, _


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        production_obj = self.env['mrp.production']
        wiz_obj = self.env['wiz.split.serials']
        productions_to_split = production_obj
        productions_no_to_split = production_obj
        for production in self:
            if (production.product_id.tracking == "serial" and
                    production.product_qty > 1):
                productions_to_split += production
            else:
                productions_no_to_split += production
        if productions_no_to_split and not productions_to_split:
            return super(MrpProduction, self).action_confirm()
        if productions_no_to_split:
            super(MrpProduction, productions_no_to_split).action_confirm()
        vals = {'mrp_production_ids': [(6, 0, productions_to_split.ids)]}
        wiz = wiz_obj.with_context(
            default_productions=productions_to_split).create(vals)
        context = self.env.context.copy()
        context["default_productions"] = [(6, 0, productions_to_split.ids)]
        return {
            'name': _("MOs to split"),
            'view_mode': 'form',
            'res_model': 'wiz.split.serials',
            'domain': [('id', '=', wiz.id)],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def split_by_serials(self):
        qty = self.product_qty
        cont = 1
        old_name = self.name
        name = "{}-{}".format(old_name, str(cont).rjust(3, "0"))
        self.write({'product_qty': 1,
                    'name': name})
        self._onchange_move_raw()
        while qty > 1:
            qty -= 1
            cont += 1
            name = "{}-{}".format(old_name, str(cont).rjust(3, "0"))
            new_production = self.copy({'name': name})
