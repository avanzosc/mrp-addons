from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    verification_by = fields.Selection([
        ('unverified', 'Unverified'),
        ('sent', 'Sent'),
        ('prototype', 'By Prototype'),
        ('antiquity', 'By Antiquity'),
        ('plan', 'By Plan')
    ], string='Verification By')
    preparation = fields.Selection([
        ('closed_box', 'Closed Box'),
        ('open_box', 'Open Box'),
        ('only_bodies', 'Only Bodies'),
        ('only_lids', 'Only Lids'),
        ('only_fronts', 'Only Fronts'),
        ('no_preparation', 'No Preparation')
    ], string='Preparation')
