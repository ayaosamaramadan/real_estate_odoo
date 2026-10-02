from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True)