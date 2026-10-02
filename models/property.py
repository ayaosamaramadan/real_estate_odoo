from odoo import models, fields, api
from odoo.exceptions import AccessError


class Property(models.Model):
    _name = "real_estate_p.property"
    _description = "Real Estate Property"

    name = fields.Char(required=True)
    description = fields.Text(string="Description")
    available = fields.Boolean(string="Available", default=True)
    price = fields.Float(string="Price", default=0.0)
    deposit = fields.Float(string="Deposit", default=0.0)
    bedrooms = fields.Integer(string="Bedrooms", default=1)
    property_type = fields.Selection([
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('office', 'Office'),
        ('land', 'Land'),
        ('shop', 'Shop'),
        ('villa', 'Villa')
    ], required=True)

    agent_id = fields.Many2one('res.users', string='Agent')

    lease_ids = fields.One2many(
        'real_estate_p.lease', 'property_id', string='Leases')

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

    def get_agent_name(self):
        for record in self:
            if record.agent_id:
                record.write({'description': record.agent_id.name})

    def inc_deposit(self):
        for record in self:
            record.deposit += 5000

    def inc_bedroom(self):
        for record in self:
            record.write({'bedrooms': record.bedrooms + 1})

    def create(self, vals):
        vals['agent_id'] = self.env.user.id
        if 'available' not in vals:
            vals['available'] = True
        if 'bedrooms' not in vals:
            vals['bedrooms'] = 1
        return super(Property, self).create(vals)

    def write(self, vals):
        if any(record.agent_id and record.agent_id != self.env.user for record in self):
            raise AccessError('You can only modify your own properties.')
        vals['agent_id'] = self.env.user.id
        return super(Property, self).write(vals)

