# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, api, _
import base64
import tempfile
import math

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None


class MrpBomImport(models.Model):
    _name = 'mrp.bom.import'

    @api.depends('filename', 'file_date')
    def _get_import_name(self):
        for file_import in self:
            file_import.name = u'{} - {}'.format(file_import.filename,
                                                 file_import.file_date)
    products_count = fields.Float(compute='_compute_products_count',
                                  string='Total Products')
    bom_count = fields.Float(compute='_compute_products_count',
                             string='Total BoMs')
    name = fields.Char(string='Import name', compute='_get_import_name')
    data = fields.Binary('File', required=True)
    filename = fields.Char('Filename')
    file_date = fields.Date(string="File Import Date", required=True,
                            default=fields.Date.context_today)
    bom_import_lines = fields.One2many(
        comodel_name='mrp.bom.line.import', inverse_name='bom_import_id',
        string='BoM Import Lines'
    )

    def _compute_products_count(self):
        if self.bom_import_lines:
            self.products_count = len(
                set(self.mapped("bom_import_lines.product_id").ids))
            self.bom_count = len(
                set(self.mapped("bom_import_lines.bom_id").ids))
        else:
            self.products_count = 0
            self.bom_count = 0

    def action_bom_import_products(self):
        views = [
            (self.env.ref('product.product_product_tree_view').id, 'tree'),
            (self.env.ref('product.product_normal_form_view').id, 'form')]
        return {
            'name': _('Products'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in',
                        self.bom_import_lines.mapped("product_id").ids)],
        }

    def action_bom_import_boms(self):
        views = [
            (self.env.ref('mrp.mrp_bom_tree_view').id, 'tree'),
            (self.env.ref('mrp.mrp_bom_form_view').id, 'form')]
        return {
            'name': _('Products'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.bom',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in',
                        self.bom_import_lines.mapped("bom_id").ids)],
        }

    def check_number(self, number):
        try:
            if isinstance(number, float) or isinstance(number, int):
                return number
            if "." in number:
                val = float(number)
            else:
                val = int(number)
            return val
        except ValueError:
            return False

    def float2string(self, number):
        if isinstance(number, float):
            if math.fmod(number, 1) == 0.0:
                return str(number).replace('.0', '')
        return str(number)

    def check_product(self, name, default_code, weight=False, map_number=False,
                      category_id=False, origin=False):
        product_obj = self.env['product.product']
        product_category = self.env['product.category']
        supplierinfo_obj = self.env['product.supplierinfo']
        route_obj = self.env['stock.location.route']
        wh_obj = self.env['stock.warehouse']
        if not name and not default_code:
            return False
        sub_name = product = False
        if default_code:
            sub_name = product_obj.search([('name', 'ilike', default_code)],
                                          limit=1)
            product = product_obj.search([('default_code', '=', default_code)],
                                         limit=1)
        if sub_name:
            return False
        if not product and name:
            product = product_obj.search(([('name', '=', name)]), limit=1)
        if not product:
            vals = {'name': name,
                    'default_code': default_code,
                    'type': 'product',
                    'weight': weight,
                    'map_number': map_number,
                    }
            if category_id:
                vals['categ_id'] = category_id
            if origin and (origin == 'F' or origin == 'C'):
                if origin == 'F':
                    route_id = wh_obj._find_global_route(
                        'mrp.route_warehouse0_manufacture',
                        _('Manufacture')).id
                if origin == 'C':
                    route_id = wh_obj._find_global_route(
                        'purchase_stock.route_warehouse0_buy', _('Buy')).id
                vals['route_ids'] = [(6, 0, [route_id])]
            product = product_obj.create(vals)
        if category_id:
            category = product_category.browse(category_id)
            if category.supplier_id:
                sup_info = supplierinfo_obj.search(
                    [('product_id', '=', product.id),
                     ('product_tmpl_id', '=',  product.product_tmpl_id.id),
                     ('name', '=', category.supplier_id.id)])
                if not sup_info:
                    supplierinfo_obj.create(
                        {'product_id': product.id,
                         'product_tmpl_id': product.product_tmpl_id.id,
                         'name': category.supplier_id.id})
        return product.id

    def check_categ(self, name):
        product_categ_obj = self.env['product.category']
        if not name:
            return False
        categ_lst = product_categ_obj.search([('name', '=', name)], limit=1)
        if not categ_lst:
            return False
        else:
            return categ_lst.id

    def action_import_bom(self):
        for line in self.bom_import_lines:
            line.unlink()
        """Load BoM lines data from the xls file."""
        file_1 = base64.decodestring(self.data)
        (fileno, fp_name) = tempfile.mkstemp('.xls', 'odoo_')
        outFile = open(fp_name, 'wb')
        outFile.write(file_1)
        outFile.close()
        reader = xlrd.open_workbook(fp_name)
        sheet = reader.sheet_by_index(0)
        ctx = self.env.context
        bom_import_line_obj = self.env['mrp.bom.line.import']
        keys = ['null', 'item', 'qty', 'code', 'map', 'name', 'weight',
                'qty_total', 'denomination', 'weight2', 'parent_code',
                'origin', 'category'
                ]
        reader.nrow = 1
        for counter in range(1, sheet.nrows-1):
            # grab the current row
            rowValues = sheet.row_values(counter+1, 0, end_colx=sheet.ncols)
            values = dict(zip(keys, rowValues))
            line_data = {
                'bom_import_id': self.id,
                'product_name': values['name'],
                'quantity': self.check_number(values['qty']) or 0,
                'product_ref': self.float2string(values['code']),
                #'map': self.float2string(values['map']),
                #'weight': self.check_number(values['weight']) or 0,
                #'origin': values['origin'],
                'bom_code': values['parent_code'],
                'categ_name': values['category'],
                }
            try:
                bom_import_line_obj.create(line_data)
            except Exception as error:
                raise exceptions.Warning(u"Line Error: \n")

    def action_validate_lines(self):
        product_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        for line in self.bom_import_lines.filtered(
                lambda x: x.state not in ('done', 'pass')):
            category_id = False
            if line.categ_name:
                category_id = self.check_categ(line.categ_name)
                if category_id:
                    line.category_id = category_id
            if not category_id:
                line.state = 'error'
                line.log_info = 'Error: Category not found'
                continue
            if not line.product_id and (line.product_ref or line.product_name):
                product_id = self.check_product(line.product_name,
                                                line.product_ref,
                                                line.weight,
                                                line.map,
                                                line.category_id.id,
                                                line.origin
                                                )
                line.product_id = product_id
                line.state = 'pass'
            elif line.product_id:
                line.state = 'pass'
            else:
                line.state = 'error'
                line.log_info = 'Error: Cannot assign product'
                continue
            if line.bom_code:
                bom = bom_obj.search([('code', '=', line.bom_code)])
                if bom:
                    line.state = 'error'
                    line.log_info = 'Error: BoM already exist'
                    continue
                bom_product = product_obj.search([('default_code', '=',
                                                   line.bom_code)])
                if not bom_product:
                    line.state = 'error'
                    line.log_info = 'Error: BoM product does not exist'
                    continue
            if not line.quantity:
                line.state = 'error'
                line.log_info = 'Error: Quantity cannot be 0'

    def action_process_lines(self):
        bom_obj = self.env['mrp.bom']
        bom_line_obj = self.env['mrp.bom.line']
        product_obj = self.env['product.product']
        for line in self.bom_import_lines.filtered(
                lambda x: x.state == 'pass'):
            bom_product = product_obj.search(
                [('default_code', '=', line.bom_code)], limit=1)
            if not bom_product:
                line.state = 'error'
                line.log_info = 'Error: BoM product does not exist'
                break
            bom = bom_obj.search(
                [('code', '=', line.bom_code)], limit=1)
            if not bom:
                bom = bom_obj.create(
                    {'code': line.bom_code,
                     'product_tmpl_id': bom_product.product_tmpl_id.id,
                     'product_id':  bom_product.id})
            bom_line = bom_line_obj.search(
                [('product_id', '=', line.product_id.id),
                 ('bom_id', '=', bom.id)], limit=1)
            if not bom_line:
                bom_line = bom_line_obj.create(
                    {'product_id': line.product_id.id,
                     'product_qty': line.quantity, 'bom_id': bom.id})
            line.bom_id = bom.id
            line.state = 'done'
            line.log_info = ''


class MrpBomLineImport(models.Model):
    _name = 'mrp.bom.line.import'

    bom_import_id = fields.Many2one(
        comodel_name='mrp.bom.import', string='BoM Import', ondelete='cascade',
        required=True)
    quantity = fields.Float(string='Quantity')
    product_name = fields.Char(string='Product name')
    product_ref = fields.Char(string='Product code')
    product_id = fields.Many2one('product.product', string='Product')
    weight = fields.Float(string='Weight')
    # origin = fields.Char(string='Origin')
    # map = fields.Char(string='Erection Drawing')
    bom_code = fields.Char(string='BoM code')
    bom_id = fields.Many2one('mrp.bom', string='BoM')
    categ_name = fields.Char(string='Category name')
    category_id = fields.Many2one('product.category', string='Category')
    log_info = fields.Text(string='Log Info')
    state = fields.Selection([
        ('2validate', 'To validate'),
        ('pass', 'Validated'),
        ('error', 'Error'),
        ('done', 'Processed')],
        string='Import state', default='2validate'
    )
