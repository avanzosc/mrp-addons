# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class MrpWorkorderNest(models.Model):
    _name = "mrp.workorder.nest"

    name = fields.Char(string="Name", readonly=True, required=True,
                       copy=False, default='New')
    code = fields.Char(string="Code")
    main_product_id = fields.Many2one(comodel_name="product.product")
    possible_main_product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_possible_main_products")
    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter")
    possible_workcenter_ids = fields.Many2many(
        comodel_name="mrp.workcenter", compute="_compute_possible_workcenter")
    main_product_tracking = fields.Selection(
        related="main_product_id.tracking")
    lot_id = fields.Many2one(comodel_name="stock.production.lot")
    nested_line_ids = fields.One2many(comodel_name="mrp.workorder.nest.line",
                                      inverse_name="nest_id",
                                      string="Nested Lines")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ], string="State", default='draft')
    line_state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready'),
        ('progress', 'Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], compute="_compute_line_states")
    line_working_state = fields.Selection(selection=[
        ('unblocked', 'Unblocked'),
        ('blocked', 'Blocked'),
    ], compute="_compute_line_states")
    line_production_state = fields.Selection(selection=[
        ('undone', 'Undone'),
        ('done', 'Done'),
    ], compute="_compute_line_states")
    line_is_produced = fields.Boolean(compute="_compute_line_states")
    line_is_user_working = fields.Boolean(compute="_compute_line_states")

    @api.depends('main_product_id')
    def _compute_possible_main_products(self):
        for nest in self:
            product_ids = self.env['mrp.bom.line'].search(
                [('main_material', '=', True)]).mapped('product_id').ids
            if product_ids:
                nest.possible_main_product_ids = [(6, 0, product_ids)]

    @api.depends('workcenter_id')
    def _compute_possible_workcenter(self):
        for nest in self:
            workcenter_ids = self.env['mrp.workcenter'].search(
                [('nesting_required', '=', True)]).ids
            if workcenter_ids:
                nest.possible_workcenter_ids = [(6, 0, workcenter_ids)]

    def name_get(self):
        result = []
        for record in self:
            name = "{}{}{}".format(record.code or "",
                                   record.code and "/" or "",
                                   record.name)
            result.append((record.id, name))
        return result

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        for line in self.nested_line_ids:
            line.lot_id = self.lot_id.id

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'mrp.workorder.nest') or 'New'
        result = super().create(vals)
        return result

    def nest_start(self):
        for nest in self:
            if nest.state == 'draft':
                nest.state = 'ready'

    def nest_draft(self):
        for nest in self:
            if nest.state == 'ready':
                nest.state = 'draft'

    def button_finish(self):
        for nest in self:
            for nl in nest.nested_line_ids:
                if nl.is_produced and nl.state == 'progress':
                    nl.workorder_id.with_context(
                        from_nest=True).button_finish()

    def button_start(self):
        for nest in self:
            for nest_line in nest.nested_line_ids:
                wo = nest_line.workorder_id
                if not wo._check_final_product_lots():
                    UserError(_(
                        '{}: You should provide a lot/serial number for the '
                        'final product.'.format(wo.name)))
            for nl in nest.nested_line_ids:
                if nl.state != 'blocked':
                    nl.workorder_id.with_context(from_nest=True).button_start()
            nest.state = 'progress'

    def record_production(self):
        for nest in self:
            for nl in nest.nested_line_ids:
                is_user_working = nl.workorder_id.is_user_working
                is_produced = nl.workorder_id.is_produced
                if is_user_working and nl.state == 'progress' and not \
                        is_produced:
                    nl._write_lot_producing_qty()
                    wo = nl.workorder_id
                    try:
                        wo.with_context(from_nest=True).record_production()
                    except UserError as e:
                        raise UserError("{}: {}".format(wo.name, str(e)))

    def button_pending(self):
        for nest in self:
            for nl in nest.nested_line_ids:
                is_user_working = nl.workorder_id.is_user_working
                if nl.working_state != 'blocked' and is_user_working and \
                        nl.state not in ('done', 'pending', 'ready', 'cancel'):
                    nl.workorder_id.with_context(
                        from_nest=True).button_pending()

    def button_unblock(self):
        for nest in self:
            for nest_line in nest.nested_line_ids:
                if nest_line.state == 'blocked':
                    nest_line.workorder_id.with_context(
                        from_nest=True).button_unblock()

    def button_scrap(self):
        for nest in self:
            for nest_line in nest.nested_line_ids:
                if nest_line.state not in ('confirmed', 'cancel'):
                    nest_line.workorder_id.with_context(
                        from_nest=True).button_scrap()

    @api.depends('nested_line_ids')
    def _compute_line_states(self):
        for nest in self:
            state = 'done'
            working_state = 'blocked'
            production_state = 'done'
            is_produced = True
            is_user_working = True
            for wl in nest.nested_line_ids:
                if wl.state != 'done':
                    state = wl.state
                if wl.working_state != 'blocked':
                    working_state = 'unblocked'
                if wl.production_state != 'done':
                    production_state = 'undone'
                if not wl.workorder_id.is_produced:
                    is_produced = False
                if not wl.workorder_id.is_user_working:
                    is_user_working = False
            nest.line_state = state
            nest.line_working_state = working_state
            nest.line_production_state = production_state
            nest.line_is_user_working = is_user_working
            nest.line_is_produced = is_produced


class MrpWorkorderNestLine(models.Model):
    _name = "mrp.workorder.nest.line"

    nest_id = fields.Many2one(comodel_name="mrp.workorder.nest")
    related_qty_producing = fields.Float(related="workorder_id.qty_producing")
    related_finished_lot_id = fields.Many2one(comodel_name="stock.production.lot",
                                           related="workorder_id.finished_lot_id")
    qty_producing = fields.Float('Currently Produced Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'))
    finished_lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id)]")
    lot_id = fields.Many2one(comodel_name="stock.production.lot",
                             domain="[('product_id', '=', "
                                    "nest_id.main_product_id.id)]")
    workorder_id = fields.Many2one(comodel_name="mrp.workorder")
    qty_produced = fields.Float(string="Produce Quantity",
                                related="workorder_id.qty_produced")
    name = fields.Char(related="workorder_id.name", string="Name")
    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter",
                                    related="workorder_id.workcenter_id",
                                    string="Workcenter",
                                    readonly=1)
    date_planned_start = fields.Datetime(
        related="workorder_id.date_planned_start",
        string="Scheduled Date Date",
        readonly=1
    )
    production_id = fields.Many2one(comodel_name="mrp.production",
                                    related="workorder_id.production_id",
                                    string="Production",
                                    readonly=1)
    product_id = fields.Many2one(comodel_name="product.product",
                                 related="workorder_id.product_id",
                                 string="Product",
                                 readonly=1)
    qty_production = fields.Float(string="Original Production Quantity",
                                  related="workorder_id.qty_production",
                                  readonly=1)
    product_uom_id = fields.Many2one(comodel_name="uom.uom",
                                     related="workorder_id.product_uom_id",
                                     string="Unit of Measure",
                                     readonly=1)
    state = fields.Selection(string="State", related="workorder_id.state",
                             readonly=1)
    working_state = fields.Selection(related="workorder_id.working_state",
                                     readonly=1)
    production_state = fields.Selection(
        related="workorder_id.production_state", readonly=1)
    company_id = fields.Many2one(related="workorder_id.company_id")

    def update_workorder_lines(self, line_values):
        for values in line_values['to_create']:
            values.pop('raw_workorder_id')
            values.update({'workorder_id': self.workorder_id.id})
            self.env['mrp.workorder.line'].create(values)
        for line in line_values['to_delete']:
            if line in self.raw_workorder_line_ids:
                line.unlink()
            else:
                self.finished_workorder_line_ids -= line
        for line, vals in line_values['to_update'].items():
            line.write(vals)

    def _write_lot_producing_qty(self):
        for n_line in self:
            res = {}
            n_line.workorder_id.qty_producing = n_line.qty_producing
            line_values = self.workorder_id._update_workorder_lines()
            n_line.update_workorder_lines(line_values)
            if n_line.finished_lot_id:
                res.update({
                    'finished_lot_id': n_line.finished_lot_id.id,
                })
            if n_line.lot_id:
                move_line = n_line.workorder_id.raw_workorder_line_ids.filtered(
                    lambda x: x.product_id == n_line.nest_id.main_product_id)
                move_line.lot_id = n_line.lot_id
            if res:
                n_line.workorder_id.write(res)
