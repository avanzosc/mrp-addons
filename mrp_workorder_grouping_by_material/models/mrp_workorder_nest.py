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
    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter",
                                    compute="_compute_workcenter")
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
    ], string="State")
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

    @api.depends('nested_line_ids')
    def _compute_workcenter(self):
        for nest in self:
            if nest.nested_line_ids:
                nest.workcenter_id = nest.nested_line_ids[0].workcenter_id.id

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "{}{}{}".format(record.code or "",
                                   record.code and "/" or "",
                                   record.name)
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'mrp.workorder.nest') or 'New'
        result = super().create(vals)
        return result

    @api.multi
    def nest_start(self):
        for nest in self:
            if nest.state == 'draft' and nest.nested_line_ids:
                nest.state = 'ready'
            elif not nest.nested_line_ids:
                raise UserError(_("The nesting has no lines"))

    def nest_draft(self):
        for nest in self:
            if nest.state == 'ready':
                nest.state = 'draft'

    @api.multi
    def button_finish(self):
        for nest in self:
            for nl in nest.nested_line_ids:
                if nl.is_produced and nl.state == 'progress':
                    nl.workorder_id.button_finish()

    @api.multi
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
                    nl.workorder_id.button_start()
            nest.state = 'progress'

    @api.multi
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
                        if nest.lot_id:
                            main_prod_line = wo.active_move_line_ids.filtered(
                                lambda x: x.product_id == nest.main_product_id)
                            main_prod_line.lot_id = nest.lot_id
                        wo.record_production()
                    except UserError as e:
                        raise UserError("{}: {}".format(wo.name, str(e)))

    @api.multi
    def button_pending(self):
        for nest in self:
            for nl in nest.nested_line_ids:
                is_user_working = nl.workorder_id.is_user_working
                if nl.working_state != 'blocked' and is_user_working and \
                        nl.state not in ('done', 'pending', 'ready', 'cancel'):
                    nl.workorder_id.button_pending()

    @api.multi
    def button_unblock(self):
        for nest in self:
            for nest_line in nest.nested_line_ids:
                if nest_line.state == 'blocked':
                    nest_line.workorder_id.button_unblock()

    @api.multi
    def button_scrap(self):
        for nest in self:
            for nest_line in nest.nested_line_ids:
                if nest_line.state not in ('confirmed', 'cancel'):
                    nest_line.workorder_id.button_scrap()

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
    related_final_lot_id = fields.Many2one(comodel_name="stock.production.lot",
                                           related="workorder_id.final_lot_id")
    qty_producing = fields.Float('Currently Produced Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'))
    final_lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id)]")
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


    def _write_lot_producing_qty(self):
        for line in self:
            res = {}
            if line.qty_producing != line.related_qty_producing:
                res.update({
                    'qty_producing': line.qty_producing,
                })
            if line.final_lot_id != line.related_final_lot_id:
                res.update({
                    'final_lot_id': line.final_lot_id.id,
                })
            if res:
                line.workorder_id.write(res)
