from odoo import fields, models


class LeaseMaintenanceRequestWizard(models.TransientModel):
    _name = 'real_estate_p.maintenance.request.wizard'
    _description = 'Create a Lease Maintenance Request'

    lease_id = fields.Many2one(
        'real_estate_p.lease',
        string='Lease',
        required=True,
        readonly=True,
    )
    issue_type = fields.Selection([
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('air_condition', 'Air Condition'),
        ('appliance', 'Appliance'),
        ('other', 'Other'),
    ], required=True, default='other')
    description = fields.Text(required=True)
    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ], required=True, default='medium')
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    scheduled_date = fields.Date()

    def action_create_request(self):
        self.ensure_one()
        request = self.env['real_estate_p.maintenance.request'].create({
            'lease_id': self.lease_id.id,
            'name': self.lease_id.name,
            'issue_type': self.issue_type,
            'description': self.description,
            'urgency': self.urgency,
            'assigned_to': self.assigned_to.id,
            'scheduled_date': self.scheduled_date,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Request',
            'res_model': 'real_estate_p.maintenance.request',
            'view_mode': 'form',
            'views': [(
                self.env.ref(
                    'real_estate_odoo.view_maintenance_request_form'
                ).id,
                'form',
            )],
            'res_id': request.id,
            'target': 'current',
        }
