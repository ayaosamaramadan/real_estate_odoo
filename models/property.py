from odoo import models, fields, api

class Property(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(required=True)
    available = fields.Boolean(string="Available", default=True)
    
    def set_available(self):
        for record in self:
            record.available = True
            
    def set_unavailable(self):
        for record in self:
            record.available = False
