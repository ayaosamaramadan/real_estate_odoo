from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Lease(models.Model):
    _name = "real_estate_p.lease"
    _description = "Real Estate Lease"

    name = fields.Char(readonly=True, copy=False)
    property_id = fields.Many2one(
        'real_estate_p.property',
        string='Property',
        required=True,
    )
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    def lease_summary(self):
        self.ensure_one()
        return self.env.ref(
            'real_estate_odoo.action_report_lease_summary'
        ).report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'real_estate.lease') or '/'
        return super().create(vals_list)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("End date must be after start date")

    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email must be unique! This email is already registered.'),
    ]
