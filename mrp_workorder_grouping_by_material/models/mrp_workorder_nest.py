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
            if nest.state == 'draft':
                nest.state = 'ready'

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
                if nl.is_user_working and nl.state == 'progress' and not \
                        nl.is_produced:
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
                if nl.working_state != 'blocked' and nl.is_user_working and \
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
    is_user_working = fields.Boolean(related="workorder_id.is_user_working",
                                     readonly=1)
    is_produced = fields.Boolean(related="workorder_id.is_produced")

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
