# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _default_get_product_id(self):
        result = False
        product = self.env["product.product"].search(
            [("one_day_chicken", "=", True)], limit=1)
        if product:
            result = product.id
        return result

    saca_line_id = fields.Many2one(
        string="Saca Line",
        comodel_name="saca.line")
    saca_id = fields.Many2one(
        string="Saca",
        comodel_name="saca",
        related="saca_line_id.saca_id",
        store=True)
    origin_qty = fields.Float(
        string="Origin Qty",
        related="saca_line_id.origin_qty",
        store=True)
    dest_qty = fields.Float(
        related="saca_line_id.dest_qty",
        store=True)
    purchase_price = fields.Float(
        related="saca_line_id.purchase_price",
        store=True)
    purchase_unit_price = fields.Float(
        related="saca_line_id.purchase_unit_price",
        store=True)
    quartering = fields.Boolean(
        string="Quartering",
        default = False)
    reproductor_quant_ids = fields.One2many(
        string="Reproductor",
        comodel_name="stock.quant",
        compute="_compute_reproductor_quant_ids")
    batch_id = fields.Many2one(
        string="Mother",
        comodel_name="stock.picking.batch")
    origin_location_ids = fields.Many2many(
        string="Hatcheries",
        comodel_name="stock.location",
        relation="rel_production_location",
        column1="location_id",
        column2="production_id")
    product_id = fields.Many2one(default=_default_get_product_id)
    consume_qty = fields.Float(
        string="Consumed Qty",
        compute="_compute_consume_qty",
        store=True)

    @api.depends("move_line_ids", "move_line_ids.qty_done")
    def _compute_consume_qty(self):
        for production in self:
            production.consume_qty = sum(
                production.move_line_ids.mapped("qty_done"))

    def _compute_reproductor_quant_ids(self):
        for production in self:
            domain = [
                ("location_id", "in", production.origin_location_ids.ids)]
            production.reproductor_quant_ids = (
                self.env["stock.quant"].search(domain)).filtered(
                    lambda c: c.product_id.egg == True)

    @api.onchange("batch_id")
    def onchange_batch_id(self):
        self.ensure_one()
        if self.batch_id:
            self.action_generate_serial()

    def action_view_reproductor_quant_ids(self):
        context = self.env.context.copy()
        context.update({"search_default_locationgroup": 1})
        return {
            "name": _("Hatcheries"),
            "view_mode": "tree,form",
            "res_model": "stock.quant",
            "domain": [("id", "in", self.reproductor_quant_ids.ids)],
            "type": "ir.actions.act_window",
            "context": context
        }

    def action_generate_serial(self):
        self.ensure_one()
        today = fields.Date.today()
        if not self.lot_producing_id:
            super(MrpProduction, self).action_generate_serial()
            if self.batch_id:
                self.lot_producing_id.name = u'{}{}{}'.format(
                    self.batch_id.name, today.strftime('%d%m'), (
                        today.strftime('%Y')[2:]))
        if self.batch_id and self.lot_producing_id:
            self.lot_producing_id.name = u'{}{}{}'.format(
                    self.batch_id.name, today.strftime('%d%m'), (
                        today.strftime('%Y')[2:]))
