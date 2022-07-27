# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class SacaLine(models.Model):
    _inherit = "saca.line"

    production_ids = fields.One2many(
        string="Production",
        comodel_name="mrp.production",
        inverse_name="saca_line_id",
        compute = "_compute_production_ids")
    quartering_ids = fields.One2many(
        string="Quartering",
        comodel_name="mrp.production",
        inverse_name="saca_line_id",
        compute = "_compute_quartering_ids")

    def _compute_production_ids(self):
        for line in self:
            cond = [("saca_line_id", "=", line.id), (
                "quartering", "=", False)]
            production = self.env["mrp.production"].search(cond)
            line.production_ids = [(6, 0, production.ids)]

    def _compute_quartering_ids(self):
        for line in self:
            cond = [("saca_line_id", "=", line.id), (
                "quartering", "=", True)]
            quartering = self.env["mrp.production"].search(cond)
            line.quartering_ids = [(6, 0, quartering.ids)]

    def action_view_production(self):
        context = self.env.context.copy()
        context.update({'default_saca_line_id': self.id})
        return {
            'name': _("Production"),
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'domain': ["|", ('id', 'in', self.production_ids.ids),
                       ("id", "in", self.quartering_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': context
        }

    def action_next_stage(self):
        super(SacaLine, self).action_next_stage()
        stage_clasificado = self.env.ref("custom_descarga.stage_clasificado")
        stage_despiece = self.env.ref("custom_descarga.stage_despiece")
        if self.stage_id == stage_despiece and not self.quartering_ids:
            prod = self.env.ref("custom_mrp_descarga.quartering_product")
            self.env["mrp.production"].create(
                    {"product_id": prod.id,
                     "quartering": True,
                     "saca_line_id": self.id,
                     "product_uom_id": prod.uom_id.id})
        if self.stage_id == stage_clasificado:
            for line in (
                self.move_line_ids.filtered(
                    lambda c: not c.move_id.sale_line_id)):
                bom = self.env["mrp.bom"].search(
                    [("product_tmpl_id", "=", (
                        line.product_id.product_tmpl_id.id))], limit=1)
                production = self.env["mrp.production"].create({
                    "bom_id": bom.id,
                    "product_id": line.product_id.id,
                    "product_uom_id": line.product_uom_id.id,
                    "product_qty": line.qty_done,
                    "saca_line_id": self.id,
                    "lot_producing_id": line.lot_id.id,
                    })
                production._onchange_move_raw()
                production.action_confirm()
                for move in production.move_raw_ids:
                    result = move.action_show_details()
                    result["context"]["default_lot"] = line.lot_id.id
                    exist_lot = self.env["stock.production.lot"].search(
                        [("product_id", "=", move.product_id.id),
                         ("name", "=", line.lot_id.name)], limit=1)
                    if exist_lot:
                        move.move_line_ids.lot_id = exist_lot.id
                    else:
                        move.move_line_ids.lot_id = self.action_create_lot(
                            move.product_id, line.lot_id.name, (
                                move.company_id)).id
                self.production_ids = [(4, production.id)]
                for move in production.move_line_ids:
                    move.onchange_product_id()
                    move.onchange_standard_price()
