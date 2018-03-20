# -*- coding: utf-8 -*-
# Copyright 2018 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, models, fields
from openerp.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = 'res.partner'

    external_laboratory = fields.Boolean(string='External Laboratory')


class QcTest(models.Model):

    _inherit = 'qc.test'

    test_type = fields.Selection(
        selection=[('internal', 'Internal'), ('external', 'External')],
        string='Test Type', default='internal')
    external_laboratory_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='qc_test_res_partner_laboratory_rel',
        column1='qc_test_id', column2='laboratory_id',
        string='External Laboratories')

    @api.multi
    @api.constrains('test_type', 'external_laboratory')
    def _check_external_laboratories(self):
        for record in self:
            if (record.test_type == 'external' and not
                    record.external_laboratory_ids):
                raise ValidationError(_('Define at least one external '
                                        'laboratory for external tests.'))


class QcInspection(models.Model):

    _inherit = 'qc.inspection'

    @api.multi
    def _make_inspection(self, object_ref, trigger_line):
        if object_ref.picking_id:
            purchase = object_ref.picking_id.sample_order
            if (object_ref.picking_id.is_external_laboratory_picking() and
                    purchase and
                    purchase.qc_test_id.id != trigger_line.test.id):
                return True
        return super(QcInspection, self)._make_inspection(object_ref,
                                                          trigger_line)
