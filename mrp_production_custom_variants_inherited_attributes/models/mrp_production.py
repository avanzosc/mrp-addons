# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# Copyright 2019 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, exceptions, _


class MrpProductionAttribute(models.Model):
    _name = 'mrp.production.attribute'
    _inherit = "product.attribute.line"

    mrp_production = fields.Many2one(comodel_name='mrp.production',
                                     string='Manufacturing Order')
    product_tmpl_id = fields.Many2one(related="mrp_production.product_tmpl_id")


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_id = fields.Many2one(required=False)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product', readonly=True,
        related=False, states={'draft': [('readonly', False)]})
    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Product Version")
    version_value_ids = fields.One2many(
        comodel_name="product.version.line",
        related="product_version_id.custom_value_ids")
    custom_value_ids = fields.One2many(
        comodel_name="production.product.version.custom.line",
        string="Custom Values",
        inverse_name="line_id", copy=True)
    product_attribute_ids = fields.One2many(
        comodel_name='mrp.production.attribute', inverse_name='mrp_production',
        string='Product attributes', copy=True, readonly=True,
        states={'draft': [('readonly', False)]},)

    def write(self, values):
        res = super().write(values)
        return res

    def _generate_raw_moves(self):
        self.ensure_one()
        moves = self.env['stock.move']
        for line in self.product_line_ids:
            if line.product_id.type in ('consu', 'product'):
                data = self._get_raw_move_dict(line)
                moves += moves.create(data)
        return moves

    def _all_custom_lines_filled(self):
        for custom in self.custom_value_ids:
            if not str(custom.custom_value) or custom.custom_value is None:
                return False
        return True

    def _all_attribute_lines_filled(self):
        for value in self.product_attribute_ids:
            if not str(value.value_id):
                return False
        return True

    def create_product_product(self):
        product_obj = self.env['product.product']
        product_id = product_obj._product_find(self.product_tmpl_id,
                                               self.product_attribute_ids)
        if not product_id and self._all_attribute_lines_filled():
            product_dict = product_obj.get_product_dict(
                self.product_tmpl_id, self.product_attribute_ids)
            self.product_id = product_obj.create(product_dict)

    def create_product_version(self):
        if self.product_id and not self.product_version_id and \
                self._all_custom_lines_filled():
            version_obj = self.env['product.version']
            version_dict = self.product_version_id.get_version_dict(
                self.product_id, self.custom_value_ids)
            self.product_version_id = version_obj.create(version_dict)

    def _delete_product_attribute_ids(self):
        delete_values = []
        for value in self.product_attribute_ids:
            delete_values.append((2, value.id))
        return delete_values

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super().onchange_product_id()
        if self.product_id:
            self.custom_value_ids = self._delete_custom_lines()
            self.product_attribute_ids = self._delete_product_attribute_ids()
            bom_obj = self.env['mrp.bom']
            product = self.product_id
            if not self.bom_id:
                self.bom_id = bom_obj._bom_find(
                    product_tmpl=product.product_tmpl_id)

            self.product_attribute_ids = \
                product._get_product_attributes_values_dict()

            self.custom_value_ids = self._set_custom_lines()
            version = self.product_id._find_version(self.custom_value_ids)
            self.product_version_id = version
            self.routing_id = self.bom_id.routing_id.id or False
        return result

    def _delete_custom_lines(self):
        delete_values = []
        for value in self.custom_value_ids:
            delete_values.append((2, value.id))
        return delete_values

    def _set_custom_lines(self):
        if self.product_version_id:
            return self.product_version_id.get_custom_value_lines()
        elif self.product_id:
            return self.product_id.get_custom_value_lines()

    @api.onchange('product_version_id')
    def product_version_id_change(self):
        if self.product_version_id:
            self.product_id = self.product_version_id.product_id
        self.custom_value_ids = self._delete_custom_lines()
        self.custom_value_ids = self._set_custom_lines()

    @api.multi
    def _onchange_bom_id(self):
        res = super(MrpProduction, self)._onchange_bom_id()
        if self.bom_id:
            bom = self.bom_id
            if bom.product_id:
                self.product_id = bom.product_id.id
            else:
                self.product_tmpl_id = bom.product_tmpl_id.id
            if 'domain' not in res:
                res['domain'] = {}
            res['domain']['routing_id'] = [('id', '=', bom.routing_id.id)]
        return res

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_template(self):
        self.ensure_one()
        self.product_attribute_ids = \
            self._delete_product_attribute_ids()
        self.custom_value_ids = self._delete_custom_lines()
        if self.product_tmpl_id:
            self.product_uom = self.product_tmpl_id.uom_id
            if (not self.product_tmpl_id.attribute_line_ids and
                    not self.product_id):
                self.product_id = (
                    self.product_tmpl_id.product_variant_ids and
                    self.product_tmpl_id.product_variant_ids[0])
                self.product_attribute_ids = (
                    self.product_id._get_product_attributes_values_dict())
            self.product_attribute_ids = (
                self.product_tmpl_id._get_product_attributes_dict())
            self.bom_id = self.env['mrp.bom']._bom_find(
                product_tmpl=self.product_tmpl_id)
            self.routing_id = self.bom_id.routing_id
            return {'domain': {'product_id':
                               [('product_tmpl_id', '=',
                                 self.product_tmpl_id.id)],
                               'bom_id':
                               [('product_tmpl_id', '=',
                                 self.product_tmpl_id.id)]}}
        return {'domain': {}}

    @api.onchange('product_attribute_ids')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        product_tmpl_id = self.product_tmpl_id
        self.product_id = product_obj._product_find(self.product_tmpl_id,
                                                    self.product_attribute_ids)
        self.product_tmpl_id = product_tmpl_id

    def get_production_model_id(self):
        params = self.env.context.get('params', {})
        if not (params and params.get('model') and params.get('id')):
            params.update({
                'model': 'mrp.production',
                'id': self.id,
            })
        return params

    @api.multi
    def button_plan(self):
        params = self.get_production_model_id()
        results = super(MrpProduction, self.with_context(
            params=params)).button_plan()
        return results

    @api.multi
    def action_compute(self):
        params = self.get_production_model_id()
        results = super(MrpProduction, self.with_context(
            params=params)).action_compute()
        return results

    @api.multi
    def _action_compute_lines(self):
        params = self.get_production_model_id()
        results = self.with_context(
            params=params)._action_compute_lines_variants()
        return results

    @api.multi
    def action_explode(self):
        params = self.get_production_model_id()
        results = super(MrpProduction, self.with_context(
            params=params)).action_explode()
        return results

    @api.multi
    def _action_compute_lines_variants(self):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """
        results = []
        bom_obj = self.env['mrp.bom']
        product_obj = self.env['product.product']
        prod_line_obj = self.env['mrp.production.product.line']

        # workcenter_line_obj = self.env['mrp.production.workcenter.line']
        for production in self:
            uom_id = self.env['uom.uom'].browse(production.product_uom_id.id)
            #  unlink product_lines
            production.product_line_ids.unlink()
            #  unlink workcenter_lines
            # production.workcenter_lines.unlink()
            #  search BoM structure and route
            bom_id = production.bom_id
            if not bom_id:
                if not production.product_id:
                    bom_id = bom_obj._bom_find(
                        product_tmpl=production.product_tmpl_id)
                else:
                    bom_id = bom_obj._bom_find(
                        product=production.product_id)
                if bom_id:
                    routing_id = bom_id.routing_id.id or False
                    self.write({'bom_id': bom_id.id,
                                'routing_id': routing_id})
            if not bom_id:
                raise exceptions.Warning(
                    _('Error! Cannot find a bill of material for this'
                      ' product.'))

            # get components and workcenter_lines from BoM structure
            factor = uom_id._compute_quantity(production.product_qty,
                                              bom_id.product_uom_id)
            # product_lines, workcenter_lines
            results, results2 = bom_id.with_context(
                production=production).explode(production.product_id,
                                               factor / bom_id.product_qty)

            #  reset product_lines in production order
            for done_line, line in results2:
                attributes = list(map(lambda x: x[2],
                                      line['product_attribute_ids']))
                product_id = (done_line.product_id or
                              product_obj._product_find(
                                  done_line.product_tmpl_id, attributes) or
                              product_obj)
                product_tmpl_id = \
                    product_id.product_tmpl_id or done_line.product_tmpl_id
                production_product_line = {
                    'name': product_id.name or done_line.product_tmpl_id.name,
                    'production_id': production.id,
                    'bom_line_id': done_line.id,
                    'product_attribute_ids': line['product_attribute_ids'],
                    'product_tmpl_id': product_tmpl_id.id,
                    'product_id': product_id.id,
                    'product_qty': line['qty'],
                    'product_uom_id': done_line.product_uom_id.id,
                    'custom_value_ids': line['custom_value_ids']
                }
                prod_line_obj.create(production_product_line)

            #  reset workcenter_lines in production order
            # for line in results2:
            #     line['production_id'] = production.id
            #     workcenter_line_obj.create(line)
        return results

    @api.multi
    def _check_create_production_product(self):
        if not self.product_tmpl_id and not self.product_id:
            raise exceptions.Warning(
                _("You can not confirm without product or variant defined."))
        if not self.product_id:
            product_obj = self.env['product.product']
            att_values_ids = [
                attr_line.value_id and attr_line.value_id.id or False
                for attr_line in self.product_attribute_ids]
            domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
            for value in att_values_ids:
                if not value:
                    raise exceptions.Warning(
                        _("You can not confirm before configuring all"
                          " attribute values."))
                domain.append(('attribute_value_ids', '=', value))
            product = product_obj.search(domain)
            if not product:
                product = product_obj.create(
                    {'product_tmpl_id': self.product_tmpl_id.id,
                     'attribute_value_ids': [(6, 0, att_values_ids)]})
            self.product_id = product

    @api.multi
    def _check_create_scheduled_product_lines_product(self, line):
        if not line.product_id:
            product_obj = self.env['product.product']
            att_values_ids = [attr_line.value_id.id or False
                              for attr_line in line.product_attribute_ids]
            domain = [('product_tmpl_id', '=', line.product_tmpl_id.id)]
            for value in att_values_ids:
                if not value:
                    raise exceptions.Warning(
                        _("You can not confirm before configuring all"
                          " attribute values."))
                domain.append(('attribute_value_ids', '=', value))
            product = product_obj.search(domain)
            if not product:
                product = product_obj.create(
                    {'product_tmpl_id': line.product_tmpl_id.id,
                     'attribute_value_ids': [(6, 0, att_values_ids)]})
            line.product_id = product
        return True

    @api.multi
    def button_confirm(self):
        self._check_create_production_product()
        for line in self.product_line_ids:
            if not self._check_create_scheduled_product_lines_product(line):
                raise exceptions.UserError(_("Scheduled lines checking error"))
        return super(MrpProduction,
                     self).button_confirm()

    def _compute_product_uom_qty(self):
        for production in self:
            if production.state == 'draft' and not production.product_id:
                production.product_uom_qty = production.product_qty
            else:
                super(MrpProduction, production)._compute_product_uom_qty()


class MrpProductionProductLineAttribute(models.Model):
    _inherit = 'product.attribute.line'
    _name = 'mrp.production.product.line.attribute'

    product_line = fields.Many2one(
        comodel_name='mrp.production.product.line',
        string='Product line')
    product_tmpl_id = fields.Many2one(related='product_line.product_tmpl_id')

    @api.one
    def _get_parent_value(self):
        if self.attribute_id.parent_inherited:
            production = self.product_line.production_id
            for attr_line in production.product_attribute_ids:
                if attr_line.attribute_id == self.attribute_id:
                    self.value_id = attr_line.value_id

# class MrpProductionProductLineAttribute(models.Model):
#     _name = 'mrp.production.product.line.attribute'
#
#     product_line = fields.Many2one(
#         comodel_name='mrp.production.product.line',
#         string='Product line')
#     attribute_id = fields.Many2one(comodel_name='product.attribute',
#                                 string='Attribute')
#     value_id = fields.Many2one(comodel_name='product.attribute.value',
#                             domain="[('attribute_id', '=', attribute_id),"
#                             "('id', 'in', possible_value_ids)]",
#                             string='Value')
#     possible_value_ids = fields.Many2many(
#         comodel_name='product.attribute.value',
#         compute='_get_possible_attribute_values')
#
#     @api.one
#     def _get_parent_value(self):
#         if self.attribute_id.parent_inherited:
#             production = self.product_line.production_id
#             for attr_line in production.product_attribute_ids:
#                 if attr_line.attribute_id == self.attribute_id:
#                     self.value_id = attr_line.value_id
#
#     @api.one
#     @api.depends('attribute_id')
#     def _get_possible_attribute_values(self):
#         attr_values = self.env['product.attribute.value']
#         template = self.product_line.product_tmpl_id
#         for attr_line in template.attribute_line_ids:
#             if attr_line.attribute_id.id == self.attribute_id.id:
#                 attr_values |= attr_line.value_ids
#         self.possible_value_ids = attr_values.sorted()


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    product_id = fields.Many2one(required=False)
    product_tmpl_id = fields.Many2one(comodel_name='product.template',
                                      string='Product')
    product_attribute_ids = fields.One2many(
        comodel_name='mrp.production.product.line.attribute',
        inverse_name='product_line', string='Product attributes',
        copy=True)
    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Product Version")
    version_value_ids = fields.One2many(
        comodel_name="product.version.line",
        related="product_version_id.custom_value_ids")
    custom_value_ids = fields.One2many(
        comodel_name="mrp.production.product.version.custom.line",
        string="Custom Values",
        inverse_name="line_id", copy=True)

    # possible_attribute_ids = fields.Many2many(
    #     comodel_name="product.attribute",
    #     compute="_compute_possible_attribute_ids")
    #
    # @api.depends("product_id")
    # def _compute_possible_attribute_ids(self):
    #     for line in self:
    #         attribute_ids = line.product_id.get_custom_attributes()
    #         line.possible_attribute_ids = [(6, 0, attribute_ids)]
    def _all_attribute_lines_filled(self):
        for value in self.product_attribute_ids:
            if not str(value.value_id):
                return False
        return True

    def get_product_dict(self, tmpl_id, attributes):
        values = attributes.mapped("value_id.id")
        return {
            'product_tmpl_id': tmpl_id.id,
            'attribute_value_ids': [(6, 0, values)],
            'active': tmpl_id.active,
        }

    def create_product_product(self):
        product_obj = self.env['product.product']
        product_id = product_obj._product_find(self.product_tmpl_id,
                                               self.product_attribute_ids)
        if not product_id and self._all_attribute_lines_filled():
            product_dict = product_obj.get_product_dict(
                self.product_tmpl_id, self.product_attribute_ids)
            self.product_id = product_obj.create(product_dict)

    def _delete_product_attribute_ids(self):
        delete_values = []
        for value in self.product_attribute_ids:
            delete_values.append((2, value.id))
        return delete_values

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super()._onchange_product_id()
        if self.product_id:
            self.custom_value_ids = self._delete_custom_lines()
            self.product_attribute_ids = self._delete_product_attribute_ids()
            product = self.product_id

            self.product_attribute_ids = \
                product._get_product_attributes_values_dict()

            self.custom_value_ids = self._set_custom_lines()
            version = self.product_id._find_version(self.custom_value_ids)
            self.product_version_id = version
        return result

    def _delete_custom_lines(self):
        delete_values = []
        for value in self.custom_value_ids:
            delete_values.append((2, value.id))
        return delete_values

    def _set_custom_lines(self):
        if self.product_version_id:
            return self.product_version_id.get_custom_value_lines()
        elif self.product_id:
            return self.product_id.get_custom_value_lines()

    @api.onchange('product_version_id')
    def product_version_id_change(self):
        for value in self.custom_value_ids:
            self.custom_value_ids = [(2, value)]
        if self.product_version_id:
            self.product_id = self.product_version_id.product_id
        self.custom_value_ids = self._set_custom_lines()

    @api.onchange('product_tmpl_id')
    def onchange_product_template(self):
        if self.product_tmpl_id:
            product_id = self.env['product.product']
            if not self.product_tmpl_id.attribute_line_ids:
                product_id = (self.product_tmpl_id.product_variant_ids and
                              self.product_tmpl_id.product_variant_ids[0])
                product_attributes = (
                    product_id._get_product_attributes_values_dict())
            else:
                product_attributes = (
                    self.product_tmpl_id._get_product_attributes_dict())
            self.name = product_id.name or self.product_tmpl_id.name
            self.product_uom = self.product_tmpl_id.uom_id
            self.product_id = product_id
            self.product_attribute_ids = product_attributes

    @api.onchange('product_attribute_ids')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        self.product_id = product_obj._product_find(
            self.product_tmpl_id, self.product_attribute_ids)


class MrpProductionProductVersionCustomLine(models.Model):
    _inherit = "version.custom.line"
    _name = "mrp.production.product.version.custom.line"

    line_id = fields.Many2one(comodel_name="mrp.production.product.line")


class ProductionProductVersionCustomLine(models.Model):
    _inherit = "version.custom.line"
    _name = "production.product.version.custom.line"

    line_id = fields.Many2one(comodel_name="mrp.production")
