# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SacaLine(models.Model):
    _inherit = "saca.line"

    production_ids = fields.One2many(
        string="Production",
        comodel_name="mrp.production",
        inverse_name="saca_line_id",
        compute="_compute_production_ids")
    count_production = fields.Integer(
        string="Count Production",
        compute="_compute_count_production")

    def _compute_count_production(self):
        for line in self:
            line.count_production = len(line.production_ids)

    def _compute_production_ids(self):
        for line in self:
            cond = [("saca_line_id", "=", line.id), (
                "quartering", "=", False)]
            production = self.env["mrp.production"].search(cond)
            line.production_ids = [(6, 0, production.ids)]

    def action_view_production(self):
        context = self.env.context.copy()
        context.update({'default_saca_line_id': False,
                        "production_id": self.production_ids[0].id,
                        "active_model": "mrp.production",
                        "active_id": self.production_ids[0].id,
                        "active_ids": self.production_ids[0].ids})
        return {
            'name': _("Production"),
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'domain': [('id', 'in', self.production_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': context,
        }

    def action_next_stage(self):
        super(SacaLine, self).action_next_stage()
        stage_clasificado = self.env.ref("custom_descarga.stage_clasificado")
        project = self.env.ref("custom_saca_timesheet.project_saca")
        if self.company_id != self.env.company:
            raise ValidationError(
                _("The company of the saca and your company is not the same."))
        if self.stage_id == stage_clasificado:
            for line in (
                self.move_line_ids.filtered(
                    lambda c: not c.move_id.sale_line_id)):
                bom = self.env["mrp.bom"].search(
                    [("product_tmpl_id", "=", (
                        line.product_id.product_tmpl_id.id))], limit=1)
                new_production = self.env["mrp.production"].new({
                    "bom_id": bom.id,
                    "product_id": line.product_id.id,
                    "product_uom_id": line.product_uom_id.id,
                    "product_qty": self.net_origin,
                    "saca_line_id": self.id,
                    "lot_producing_id": line.lot_id.id,
                    "company_id": self.company_id.id
                    })
                for (
                    comp_onchange) in (
                        new_production._onchange_methods["company_id"]):
                    comp_onchange(new_production)
                vals = new_production._convert_to_write(new_production._cache)
                production = self.env["mrp.production"].create(vals)
                production.onchange_product_id()
                production._onchange_product_qty()
                production._onchange_bom_id()
                production._onchange_move_raw()
                production._check_is_deconstruction()
                production._onchange_location()
                production._onchange_location_dest()
                production._onchange_date_planned_start()
                production._onchange_move_finished_product()
                production._onchange_move_finished()
                production._onchange_lot_producing()
                production._onchange_workorder_ids()
                production._check_production_lines()
                production._create_update_move_finished()
            if self.production_ids:
                for line in self.production_ids:
                    if not line.clasified_ids:
                        self.env["project.task"].create({
                            "project_id": project.id,
                            "name": "Clasificado",
                            "production_id": line.id,
                            "timesheet_ids": [(0, 0, {
                                "production_id": line.id,
                                "date": self.unload_date.date(),
                                "name": u'{} {}'.format(
                                    project.name, "Clasificado"),
                                "project_id": project.id,
                                "classified": True})]})
                    for clas in line.clasified_ids:
                        clas.employee_id = False
                        clas.user_id = False

    @api.depends("stage_id", "production_ids")
    def _compute_stage(self):
        super(SacaLine, self)._compute_stage()
        for line in self:
            matanza = self.env.ref("custom_descarga.stage_matanza")
            clasificado = self.env.ref("custom_descarga.stage_clasificado")
            if line.stage_id == clasificado and not line.production_ids:
                line.write({
                    "stage_id": matanza.id,
                    "is_presaca": False,
                    "is_saca": False,
                    "is_descarga": False,
                    "is_killing": True,
                    "is_classified": False})

    def write(self, values):
        result = super(SacaLine, self).write(values)
        if "gross_origin" in (
            values) or "tara_origin" in (
                values) and self.net_origin:
            for line in self.production_ids:
                line.product_qty = self.net_origin
        return result
