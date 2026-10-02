from odoo import models, fields, api


class Property(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(required=True)
    description = fields.Text(string="Description")
    available = fields.Boolean(string="Available", default=True)
    price = fields.Float(string="Price", default=0.0)
    property_type = fields.Selection([
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('office', 'Office'),
        ('land', 'Land'),
        ('shop', 'Shop'),
        ('villa', 'Villa')
    ], required=True)

    def set_available(self):
        for record in self:
            record.available = True

    def set_unavailable(self):
        for record in self:
            record.available = False

    def change_property_type_to_office(self):
        for record in self:
            record.property_type = 'office'

    def update_description(self):
        for record in self:
            record.write({'description': 'This is a property desc'})

    def mark_as_occupied(self):
        for record in self:
            record.write({'available': False, 'price': record.price + 2000})
