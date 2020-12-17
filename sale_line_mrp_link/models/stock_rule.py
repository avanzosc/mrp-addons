# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        res = super()._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin,
            values, bom)
        context = self.env.context
        if 'sale_line_id' in context:
            res['sale_line_id'] = context.get('sale_line_id')
        if 'active' in self.env.context:
            res['active'] = context.get('active')
        return res

    @api.multi
    def _run_manufacture(
            self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        if not self.env.context.get("production_id", False):
            super(StockRule, self)._run_manufacture(
                product_id, product_qty, product_uom, location_id, name,
                origin, values)
        else:
            Production = self.env['mrp.production']
            ProductionSudo = Production.sudo().with_context(
                force_company=values['company_id'].id)
            production = ProductionSudo.browse(
                self.env.context.get("production_id"))
            production.write({
                "move_dest_ids": (values.get('move_dest_ids') and
                                  [(4, x.id) for x in values['move_dest_ids']]
                                  or False),
                "propagate": self.propagate,
            })
            origin_production = (
                values.get('move_dest_ids') and
                values['move_dest_ids'][0].raw_material_production_id or False)
            orderpoint = values.get('orderpoint_id')
            if orderpoint:
                production.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': production,
                            'origin': orderpoint},
                    subtype_id=self.env.ref('mail.mt_note').id)
            if origin_production:
                production.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': production,
                            'origin': origin_production},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True
