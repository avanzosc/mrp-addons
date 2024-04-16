# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from datetime import datetime
from dateutil import rrule
from _datetime import timedelta
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    saca_line_id = fields.Many2one(
        string="Saca Line",
        comodel_name="saca.line",
        copy=False)
    saca_id = fields.Many2one(
        string="Saca",
        comodel_name="saca",
        related="saca_line_id.saca_id",
        store=True,
        copy=False)
    origin_qty = fields.Float(
        string="Origin Qty",
        related="saca_line_id.net_origin",
        store=True)
    dest_qty = fields.Float(
        related="saca_line_id.net_dest",
        store=True)
    purchase_price = fields.Float(
        related="saca_line_id.purchase_price",
        store=True)
    purchase_unit_price = fields.Float(
        related="saca_line_id.purchase_unit_price",
        store=True)
    saca_date = fields.Date(
        string="Saca Date",
        related="saca_line_id.date",
        store=True)
    reproductor_quant_ids = fields.One2many(
        string="Reproductor",
        comodel_name="stock.quant",
        compute="_compute_reproductor_quant_ids")
    batch_id = fields.Many2one(
        string="Mother",
        comodel_name="stock.picking.batch",
        copy=False)
    chick_production = fields.Boolean(
        string="Chick Production",
        related="picking_type_id.chick_production",
        store=True)
    production_date = fields.Datetime(
        default=fields.Datetime.now())
    birth_week = fields.Integer(
        string="Birth Week",
        compute="_compute_birth_week",
        store=True)
    paasa = fields.Boolean(
        string="PAASA",
        related="company_id.paasa",
        store=True)
    tolvasa = fields.Boolean(
        string="Tolvasa",
        related="company_id.tolvasa",
        store=True)
    guide_number = fields.Char(
        string="Guide Number",
        related="saca_line_id.guide_number",
        store=True)
    channel_temperature = fields.Float(
        string="Channel Temperature",
        related="saca_line_id.channel_temperature",
        store=True)
    staff = fields.Integer(
        string="Staff",
        related="saca_line_id.staff",
        store=True)
    product_qty = fields.Float(
        copy=False)
    hen_unit = fields.Integer(
        string="Hen Units",
        related="batch_id.hen_unit",
        store=True)
    birth_rate = fields.Float(
        string="Birth %",
        compute="_compute_birth_rate",
        store=True)
    expected_birth = fields.Float(
        string="Expected Births",
        compute="_compute_expected_birth",
        store=True)
    expected_rate = fields.Float(
        string="Expected %",
        compute="_compute_expected_birth",
        store=True)
    birth_difference = fields.Float(
        string="Difference",
        compute="_compute_birth_difference",
        store=True)
    difference_rate = fields.Float(
        string="Difference %",
        compute="_compute_difference_rate",
        store=True)
    batch_location_id = fields.Many2one(
        string="Mother Location",
        related="batch_id.location_id",
        store=True)
    clasified_date = fields.Date(
        string="Clasified Date",
        compute="_compute_clasified_date")
    clasified_time_start = fields.Float(
        string="Clasified Time Start",
        compute="_compute_clasified_date")
    clasified_time_stop = fields.Float(
        string="Clasified Time Stop",
        compute="_compute_clasified_date")
    real_average_weight = fields.Float(
        string="Real Average Weight",
        compute="_compute_real_average_weight",
        store=True,
        digits="Weight Decimal Precision")
    unload_date = fields.Datetime(
        string="Unload Date",
        related="saca_line_id.unload_date",
        store=True)
    download_unit = fields.Integer(
        string="Download Unit",
        related="saca_line_id.download_unit",
        store=True)
    unit_difference = fields.Integer(
        string="Unit Difference",
        compute="_compute_unit_difference",
        store=True)
    total_unit = fields.Float(
        string="Units",
        compute="_compute_total_unit",
        store=True)
    average_weight = fields.Float(
        string="Average Weight",
        related="saca_line_id.average_weight_origin",
        store=True)
    gross_yield = fields.Float(
        string="Gross Yield",
        compute="_compute_gross_yield",
        store=True)
    descarga_order = fields.Char(
        string="Descarga Order",
        related="saca_line_id.descarga_order")
    produced_qty = fields.Float(
        string="Produced Qty",
        compute="_compute_produced_qty",
        store=True)
    qty_difference = fields.Float(
        string="Difference",
        compute="_compute_qty_dofference",
        store=True)
    quartering = fields.Boolean(
        string="Quartering")
    no_duplicate_lines = fields.Boolean(
        string="No Duplicate Lines",
        related="bom_id.no_duplicate_lines",
        store=True)
    bom_id = fields.Many2one(
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""")
    clasification = fields.Selection(
        string="Clasification", selection=[
            ("normal", "Normal"),
            ("relaxed", "Relaxed"),
            ("demanding", "Demanding")])
    channel_temperature = fields.Float(
        string="Channel Temperature")
    waiting_time = fields.Float(string="Waiting Time")
    clasified_ids = fields.One2many(
        string="Classified",
        comodel_name="account.analytic.line",
        inverse_name="production_id")
    farm_warehouse_id = fields.Many2one(
        string="Farm",
        comodel_name="stock.warehouse",
        related="saca_line_id.farm_warehouse_id",
        store=True)
    farm_id = fields.Many2one(
        string="Farm",
        comodel_name="res.partner",
        related="saca_line_id.farm_id",
        store=True)
    vehicle_id = fields.Many2one(
        string="Vehicle",
        comodel_name="fleet.vehicle",
        related="saca_line_id.vehicle_id",
        store=True)
    remolque_id = fields.Many2one(
        string="Remolque",
        comodel_name="fleet.vehicle",
        related="saca_line_id.remolque_id",
        store=True)
    breeding_id = fields.Many2one(
        string="Breeding",
        comodel_name="stock.picking.batch",
        related="saca_line_id.breeding_id",
        store=True)
    asphyxiation_units = fields.Integer(
        string="Asphyxiated",
        compute="_compute_asphyxiation_units",
        store=True)
    seized_units = fields.Integer(
        string="Seized",
        compute="_compute_seized_units",
        store=True)
    rto_percentage = fields.Float(
        string="Rto. %",
        compute="_compute_rto_percentage",
        store=True)
    bom_category_id = fields.Many2one(
        string="Category",
        related="bom_id.category_id",
        store=True
    )
    no_produce_product = fields.Boolean(
        string="Don't produce the header product",
        related="bom_id.no_produce_product",
        store=True
    )

    @api.depends("move_line_ids.percentage")
    def _compute_rto_percentage(self):
        for line in self:
            rto_percentage = 0
            if line.move_line_ids:
                rto_percentage = sum(
                    line.move_line_ids.mapped("percentage"))
            line.rto_percentage = rto_percentage

    @api.depends("move_line_ids.product_id",
                 "move_line_ids.product_id.chicken_seized",
                 "move_line_ids.unit", "quartering")
    def _compute_seized_units(self):
        for line in self:
            seized_units = 0
            if line.move_line_ids and line.move_line_ids.filtered(
                lambda c: c.product_id.chicken_seized) and not (
                    line.quartering):
                seized_units = sum(
                    line.move_line_ids.filtered(
                        lambda c: c.product_id.chicken_seized).mapped("unit"))
            line.seized_units = seized_units

    @api.depends("move_line_ids.product_id",
                 "move_line_ids.product_id.asphyxiated", "quartering",
                 "move_line_ids.unit")
    def _compute_asphyxiation_units(self):
        for line in self:
            asphyxiation_units = 0
            if line.move_line_ids and line.move_line_ids.filtered(
                lambda c: c.product_id.asphyxiated) and not (
                    line.quartering):
                asphyxiation_units = sum(
                    line.move_line_ids.filtered(
                        lambda c: c.product_id.asphyxiated).mapped("unit"))
            line.asphyxiation_units = asphyxiation_units

    def _compute_classified_ids(self):
        for line in self:
            cond = [("production_id", "=", line.id), (
                "classified", "=", True)]
            classified = self.env["account.analytic.line"].search(cond)
            line.clasified_ids = [(6, 0, classified.ids)]

    @api.depends("produced_qty", "consume_qty")
    def _compute_qty_dofference(self):
        for production in self:
            production.qty_difference = (
                production.consume_qty - production.produced_qty)

    @api.depends("finished_move_line_ids.qty_done")
    def _compute_produced_qty(self):
        for production in self:
            produced_qty = 0
            if production.finished_move_line_ids:
                produced_qty = sum(production.finished_move_line_ids.filtered(
                    lambda c: c.product_uom_id == production.product_uom_id
                ).mapped("qty_done"))
            production.produced_qty = produced_qty

    @api.depends("move_line_ids.qty_done", "origin_qty")
    def _compute_gross_yield(self):
        for line in self:
            gross_yield = 0
            if line.origin_qty != 0:
                gross_yield = sum(
                    line.move_line_ids.mapped("qty_done")) / line.origin_qty
            line.gross_yield = gross_yield

    @api.depends("move_line_ids.unit")
    def _compute_total_unit(self):
        for line in self:
            total_unit = 0
            if line.move_line_ids:
                total_unit = sum(line.move_line_ids.mapped("unit"))
            line.total_unit = total_unit

    @api.depends("download_unit", "move_line_ids.unit")
    def _compute_unit_difference(self):
        for line in self:
            unit_difference = line.download_unit
            if line.move_line_ids:
                unit_difference = sum(
                        line.move_line_ids.mapped("unit")) - line.download_unit
            line.unit_difference = unit_difference

    @api.depends("origin_qty", "move_line_ids.unit")
    def _compute_real_average_weight(self):
        for line in self:
            real_average_weight = 0
            units = sum(line.move_line_ids.mapped("unit"))
            if units != 0:
                real_average_weight = line.origin_qty / units
            line.real_average_weight = real_average_weight

    def _compute_clasified_date(self):
        for line in self:
            clasified_date = False
            clasified_time_start = 0
            clasified_time_stop = 0
            if line.clasified_ids:
                cl_line = line.clasified_ids[:1]
                clasified_date = cl_line.date
                clasified_time_start = cl_line.time_start
                clasified_time_stop = cl_line.time_stop
            line.clasified_date = clasified_date
            line.clasified_time_start = clasified_time_start
            line.clasified_time_stop = clasified_time_stop

    @api.depends("birth_difference", "product_qty")
    def _compute_difference_rate(self):
        for line in self:
            difference_rate = 0
            if line.product_qty != 0:
                difference_rate = (
                    line.birth_difference * 100 / line.product_qty)
            line.difference_rate = difference_rate

    @api.depends("product_qty", "expected_birth")
    def _compute_birth_difference(self):
        for line in self:
            line.birth_difference = line.product_qty - line.expected_birth

    @api.depends("batch_id.birth_rate_ids", "product_qty",
                 "production_date")
    def _compute_expected_birth(self):
        for line in self:
            expected_birth = 0
            if line.production_date:
                rate = line.batch_id.birth_rate_ids.filtered(
                    lambda c: c.birth_start_date and c.birth_start_date <= (
                        line.production_date.date()) and (
                            c.birth_start_date + timedelta(days=7)) > (
                                line.production_date.date()))
                if rate:
                    line.expected_rate = rate[0].percentage_birth
                    expected_birth = (
                        line.product_qty * rate[0].percentage_birth) / 100
            line.expected_birth = expected_birth

    @api.depends("product_qty", "consume_qty")
    def _compute_birth_rate(self):
        for line in self:
            birth_rate = 0
            if line.consume_qty != 0:
                birth_rate = line.product_qty * 100 / line.consume_qty
            line.birth_rate = birth_rate

    @api.depends("production_date")
    def _compute_birth_week(self):
        for line in self:
            week = 0
            if line.production_date:
                start_date = datetime(
                    line.production_date.year, 1, 1, 0, 0).date()
                start_date = line.calculate_weeks_start(start_date)
                end_date = line.production_date.date()
                if end_date < start_date:
                    start_date = datetime(
                        line.production_date.year - 1, 1, 1, 0, 0).date()
                    start_date = line.calculate_weeks_start(start_date)
                    end_date = datetime(
                        line.production_date.year, 1, 1, 0, 0).date()
                week = line.weeks_between(start_date, end_date)
                if week == 53:
                    week = 1
            line.birth_week = week

    def weeks_between(self, start_date, end_date):
        weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
        return weeks.count()

    def _compute_reproductor_quant_ids(self):
        for production in self:
            production.reproductor_quant_ids = (
                self.env["stock.quant"].sudo().search([])).filtered(
                    lambda c: c.product_id.egg is True and (
                        c.location_id.is_hatchery is True))

    @api.onchange("picking_type_id")
    def onchange_picking_type(self):
        result = super(MrpProduction, self).onchange_picking_type()
        product = self.env["product.product"].search(
            [("one_day_chicken", "=", True)], limit=1)
        if self.chick_production and product:
            self.product_id = product.id
        elif self.env.company.paasa:
            product = self.env["product.product"].search([
                ("download_product", "=", True)])
            if product and len(product) == 1:
                self.product_id = product.id
        else:
            self.product_id = False
        return result

    @api.onchange("batch_id", "production_date")
    def onchange_batch_id(self):
        self.ensure_one()
        if self.batch_id and self.production_date:
            self.action_generate_serial()

    @api.onchange("product_qty", "product_uom_id")
    def _onchange_product_qty(self):
        super(MrpProduction, self)._onchange_product_qty()
        if self.product_qty:
            self.qty_producing = self.product_qty

    @api.onchange("bom_id")
    def _onchange_bom_id(self):
        result = super(MrpProduction, self)._onchange_bom_id()
        if self.saca_line_id and self.origin_qty:
            self.product_qty = self.origin_qty
        if self.bom_id:
            self.quartering = self.bom_id.quartering
        return result

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    def action_emptying_hatchers(self):
        for production in self:
            if not production.batch_id:
                raise ValidationError(
                    _("No mother has been put on.")
                    )
            if not production.lot_producing_id:
                raise ValidationError(
                    _("No lot has been put on.")
                    )
            production.move_line_ids.unlink()
            for quant in production.reproductor_quant_ids:
                if (
                    quant.available_quantity > 0) and (
                        quant.lot_id.batch_id == production.batch_id):
                    line = production.move_line_ids.filtered(
                        lambda c: c.product_id == quant.product_id and (
                            c.location_id == quant.location_id) and (
                                c.lot_id == quant.lot_id))
                    if line:
                        line.qty_done += quant.available_quantity
                    if not line:
                        self.env["stock.move.line"].create(
                            {"product_id": quant.product_id.id,
                             "location_id": quant.location_id.id,
                             "location_dest_id": (
                                 production.production_location_id.id),
                             "product_uom_id": quant.product_id.uom_id.id,
                             "qty_done": quant.available_quantity,
                             "lot_id": quant.lot_id.id,
                             "batch_id": production.batch_id.id,
                             "standard_price": quant.product_id.standard_price,
                             "amount": (
                                 quant.available_quantity) * (
                                     quant.product_id.standard_price),
                             "company_id": production.company_id.id,
                             "production_id": production.id,
                             "move_id": production.move_raw_ids.filtered(
                                 lambda c: c.product_id == quant.product_id
                                 ).id})

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

    def action_confirm(self):
        super(MrpProduction, self).action_confirm()
        for production in self:
            production.action_assign_serials()

    def button_mark_done(self):
        if self.move_finished_ids:
            self.move_finished_ids._do_unreserve()
        result = super(MrpProduction, self).button_mark_done()
        if result is not True and "res_model" in result and result["res_model"] == "mrp.consumption.warning" and self.no_duplicate_lines:
            entry_qty = sum(self.move_line_ids.mapped("qty_done"))
            out_qty = sum(self.finished_move_line_ids.mapped("qty_done"))
            for move in self.move_raw_ids:
                move.product_uom_qty = entry_qty
            for move in self.move_byproduct_ids:
                move.product_uom_qty = out_qty
        if self.finished_move_line_ids:
            for line in self.finished_move_line_ids:
                values = {
                    "location_id": line.move_id.location_id.id,
                    "location_dest_id": line.move_id.location_dest_id.id
                    }
                if self.batch_id:
                    values.update({
                        "batch_id": self.batch_id.id})
                line.write(values)
        if result is True and self.no_produce_product:
            self.action_delete_producing_line()
        if self.picking_type_id.chick_production:
            for line in self.move_line_ids:
                line.onchange_standard_price()
        return result

    def action_delete_producing_line(self):
        for line in self:
            if line.no_produce_product:
                for move in line.move_finished_ids.filtered(
                    lambda c: c.product_id == (
                        line.product_id)):
                    move.do_cancel_done()
                    move.state = "cancel"

    def action_generate_serial(self):
        self.ensure_one()
        date = self.production_date.date()
        if not self.lot_producing_id:
            super(MrpProduction, self).action_generate_serial()
            if self.batch_id:
                self.lot_producing_id.name = u"{}{}{}".format(
                    self.batch_id.name, date.strftime("%d%m"), (
                        date.strftime("%Y")[2:]))
        if self.batch_id and self.lot_producing_id:
            self.lot_producing_id.name = u"{}{}{}".format(
                    self.batch_id.name, date.strftime("%d%m"), (
                        date.strftime("%Y")[2:]))
        self.lot_producing_id.batch_id = self.batch_id.id

    def action_assign_serials(self):
        for production in self:
            if production.move_line_ids and production.lot_producing_id:
                for line in production.move_line_ids:
                    if line.product_id.tracking != "none" and not (
                            line.lot_id):
                        lot = self.env["stock.production.lot"].search(
                            [("name", "=", production.lot_producing_id.name),
                             ("product_id", "=", line.product_id.id)],
                            limit=1).id
                        if not lot:
                            lot = self.env[(
                                "stock.production.lot")].action_create_lot(
                                    line.product_id,
                                    production.lot_producing_id.name,
                                    production.company_id).id
                        line.lot_id = lot

    def action_delete_moves_with_qty_zero(self):
        self.ensure_one()
        lines = self.move_line_ids.filtered(lambda c: c.qty_done == 0)
        for line in lines:
            line.unlink()

    def calculate_weeks_start(self, start_date):
        self.ensure_one()
        weekday = start_date.weekday()
        if weekday <= 3:
            return start_date - timedelta(days=weekday)
        else:
            return start_date + timedelta(days=(7-weekday))

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(MrpProduction, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for line in result:
            if '__domain' in line:
                lines = self.search(line["__domain"])
                average_weight = sum(lines.mapped("average_weight"))/len(lines)
                rto_percentage = sum(lines.mapped("rto_percentage"))/len(lines)
                purchase_unit_price = sum(lines.mapped("purchase_unit_price"))/len(lines)
                line["average_weight"] = average_weight
                line["rto_percentage"] = rto_percentage
                line["purchase_unit_price"] = purchase_unit_price
        return result
