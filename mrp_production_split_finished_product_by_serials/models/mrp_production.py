# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    initial_product_qty = fields.Float(
        string="Initial quantity to produce", default=0,
        digits='Product Unit of Measure', copy=False)

    @api.onchange('product_qty', 'product_uom_id')
    def _onchange_product_qty(self):
        qty = 0
        if (self.product_id and self.product_qty and
            self.product_id.tracking and
                self.product_id.tracking == "serial"):
            qty = self.product_qty
        self.initial_product_qty = qty

    def action_confirm(self):
        result = super(MrpProduction, self).action_confirm()
        for production in self:
            product = production.product_id
            if product.tracking and product.tracking == "serial":
                production._new_by_product_treatment_after_confirmation()
        return result

    def _new_by_product_treatment_after_confirmation(self):
        self.with_context(same_subproduct=True).action_generate_serial()
        self.lot_producing_id.name = "{}x001".format(self.name)

    def _set_qty_producing(self):
        if self.product_id.tracking and self.product_id.tracking == "serial":
            return super(
                MrpProduction, self.with_context(
                    qty_twith_serial=self.product_qty))._set_qty_producing()
        else:
            return super(MrpProduction, self)._set_qty_producing()

    def button_mark_done(self):
        if self.product_id.tracking and self.product_id.tracking == "serial":
            return super(MrpProduction, self.with_context(
                with_tracking_serial=True)).button_mark_done()
        else:
            return super(MrpProduction, self).button_mark_done()

    def write(self, vals):
        result = super(MrpProduction, self).write(vals)
        if "date_finished" in vals and vals.get("date_finished", False):
            for production in self:
                if (production.product_id.tracking and
                        production.product_id.tracking == "serial"):
                    production.create_lot_for_tracking_serial()
        return result

    def create_lot_for_tracking_serial(self):
        move = self.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id)
        new_lots = self.env['stock.production.lot']
        cont = 0
        if len(move) == 1:
            cond = [("move_id", '=', move.id)]
            line = self.env["stock.move.line"].search(cond)
            if line:
                qty_done = line.qty_done
                while cont < qty_done:
                    cont += 1
                    if cont == 1:
                        line.write({'qty_done': 1,
                                    'lot_id': self.lot_producing_id.id})
                    else:
                        name = self.lot_producing_id.name
                        if "x001" in self.lot_producing_id.name:
                            name = self.lot_producing_id.name.replace(
                                "x001", "")
                        else:
                            name = self.lot_producing_id.name
                        name = "{}x{}".format(name, str(cont).zfill(3))
                        vals_lot = {'name': name,
                                    'company_id': self.company_id.id,
                                    'product_id': self.product_id.id}
                        new_lot = self.env['stock.production.lot'].create(
                            vals_lot)
                        new_lots += new_lot
                        default = {'lot_id': new_lot.id,
                                   'qty_done': 1}
                        line.copy(default)
        cond = [('lot_id', '=', self.lot_producing_id.id),
                ('picking_id', '!=', False)]
        lines = self.env['stock.move.line'].search(cond, order = 'id asc')
        cont = 0
        for line in lines:
            cont += 1
            if cont > 1:
                line.lot_id = new_lots[cont - 2].id
