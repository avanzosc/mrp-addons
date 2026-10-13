# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=attribute-string-redundant
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SacaLine(models.Model):
    _inherit = "saca.line"

    production_ids = fields.One2many(
        string="Production",
        comodel_name="mrp.production",
        inverse_name="saca_line_id",
        compute="_compute_production_ids",
    )
    count_production = fields.Integer(
        string="Count Production", compute="_compute_count_production"
    )

    recalc_date = fields.Datetime(string="Last Quality Recalc", copy=False, store=True)

    def _compute_count_production(self):
        for line in self:
            line.count_production = len(line.production_ids)

    def _compute_production_ids(self):
        for line in self:
            cond = [("saca_line_id", "=", line.id), ("quartering", "=", False)]
            production = self.env["mrp.production"].search(cond)
            line.production_ids = [(6, 0, production.ids)]

    def action_view_production(self):
        self.ensure_one()
        production = self.production_ids[:1]
        context = self.env.context.copy()
        context.update(
            {
                "default_saca_line_id": False,
                "production_id": production.id or False,
                "active_model": "mrp.production",
                "active_id": production.id or False,
                "active_ids": production.ids,
            }
        )
        return {
            "name": _("Production"),
            "view_mode": "list,form",
            "res_model": "mrp.production",
            "domain": [("id", "in", self.production_ids.ids)],
            "search_view_id": self.env.ref("mrp.view_mrp_production_filter").id,
            "type": "ir.actions.act_window",
            "context": context,
        }

    def action_next_stage(self):
        result = super().action_next_stage()
        stage_clasificado = self.env.ref("custom_descarga.stage_clasificado")
        project = self.env.ref("custom_saca_timesheet.project_saca")
        if self.company_id != self.env.company:
            raise ValidationError(
                _("The company of the saca and your company is not the same.")
            )
        if self.stage_id == stage_clasificado:
            for line in self.move_line_ids.filtered(
                lambda c: not c.move_id.sale_line_id
            ):
                bom = self.env["mrp.bom"].search(
                    [("product_tmpl_id", "=", (line.product_id.product_tmpl_id.id))],
                    limit=1,
                )
                new_production = self.env["mrp.production"].new(
                    {
                        "bom_id": bom.id,
                        "product_id": line.product_id.id,
                        "product_uom_id": line.product_uom_id.id,
                        "product_qty": self.net_origin,
                        "saca_line_id": self.id,
                        "lot_producing_id": line.lot_id.id,
                        "company_id": self.company_id.id,
                    }
                )
                for comp_onchange in new_production._onchange_methods["company_id"]:
                    comp_onchange(new_production)
                new_production._compute_picking_type_id()
                new_production._compute_locations()
                new_production._compute_production_location()
                vals = new_production._convert_to_write(new_production._cache)
                production = self.env["mrp.production"].create(vals)
                production._onchange_product_qty()
                production._onchange_bom_id()
                production._compute_production_location()
                production._compute_locations()
                production._compute_move_raw_ids()
                production._check_is_deconstruction()
                production._compute_move_finished_ids()
                production._onchange_lot_producing()
                if production.bom_id:
                    production._compute_workorder_ids()
                for analytic in self.timesheet_ids:
                    if not analytic.mrp_production_id:
                        analytic.mrp_production_id = production.id
            if self.production_ids:
                for line in self.production_ids:
                    if not line.clasified_ids:
                        self.env["project.task"].create(
                            {
                                "project_id": project.id,
                                "name": "Clasificado",
                                "production_id": line.id,
                                "timesheet_ids": [
                                    (
                                        0,
                                        0,
                                        {
                                            "production_id": line.id,
                                            "date": self.unload_date.date(),
                                            "name": "{} {}".format(
                                                project.name, "Clasificado"
                                            ),
                                            "project_id": project.id,
                                            "classified": True,
                                        },
                                    )
                                ],
                            }
                        )
                    for clas in line.clasified_ids:
                        clas.employee_id = False
                        clas.user_id = False
        return result

    @api.depends("stage_id", "production_ids")
    def _compute_stage(self):
        result = super()._compute_stage()
        for line in self:
            matanza = self.env.ref("custom_descarga.stage_matanza")
            clasificado = self.env.ref("custom_descarga.stage_clasificado")
            if line.stage_id == clasificado and not line.production_ids:
                line.write(
                    {
                        "stage_id": matanza.id,
                        "is_presaca": False,
                        "is_saca": False,
                        "is_descarga": False,
                        "is_killing": True,
                        "is_classified": False,
                    }
                )
        return result

    def write(self, values):
        result = super().write(values)
        if "gross_origin" in (values) or "tara_origin" in (values) and self.net_origin:
            for line in self.production_ids:
                line.product_qty = self.net_origin
        return result

    def action_compute_mo_data(self):
        self.ensure_one()
        now = fields.Datetime.now()
        for line in self:
            line.recalc_date = now
            move_lines = line.mapped("production_ids.move_line_ids")
            asphyxiated = move_lines.filtered(
                lambda move_line: move_line.product_id.default_code == "8650"
            )
            seizured = move_lines.filtered(
                lambda move_line: move_line.product_id.default_code == "9020"
            )
            if line.download_unit:
                line.asphyxiated_percentage = (
                    sum(asphyxiated.mapped("unit")) / line.download_unit
                ) * 100.0
                line.seizured_percentage = (
                    sum(seizured.mapped("unit")) / line.download_unit
                ) * 100.0
            else:
                line.asphyxiated_percentage = 0.0
                line.seizured_percentage = 0.0
            line.second_percentage = sum(
                line.mapped("production_ids.second_performance")
            )
        return True
