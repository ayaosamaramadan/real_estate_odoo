from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Lease(models.Model):
    _name = 'real_estate_p.lease'
    _description = 'Property Lease Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    name = fields.Char(
        string='Lease Reference',
        required=True,
        readonly=True,
        copy=False,
        default='New',
    )
    property_id = fields.Many2one(
        'real_estate_p.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True, tracking=True)
    deposit_paid = fields.Float(string='Deposit Paid', tracking=True)
    main_ids = fields.One2many(
        'real_estate_p.maintenance.request',
        'lease_id',
        string='Maintenance Requests',
    )
    payment_ids = fields.One2many(
        'real_estate_p.lease.payment',
        'lease_id',
        string='Payments',
    )
    duration_month = fields.Integer(
        string='Duration (Months)',
        compute='_compute_duration',
        store=True,
    )
    comp_is_active = fields.Boolean(
        string='Is Active',
        compute='_compute_is_active',
    )
    next_elec_recharge = fields.Date(
        string='Next Electricity Recharge',
        compute='_compute_next_elec_recharge',
    )
    total_plumbing_cost = fields.Float(
        string='Total Plumbing Cost',
        compute='_compute_maintenance_costs',
    )
    total_electrical_cost = fields.Float(
        string='Total Electrical Cost',
        compute='_compute_maintenance_costs',
    )
    total_air_condition_cost = fields.Float(
        string='Total Air Condition Cost',
        compute='_compute_maintenance_costs',
    )
    total_appliance_cost = fields.Float(
        string='Total Appliance Cost',
        compute='_compute_maintenance_costs',
    )
    total_other_cost = fields.Float(
        string='Total Other Cost',
        compute='_compute_maintenance_costs',
    )
    next_payment_date = fields.Date(string='Next Payment Date')
    last_reminder_sent = fields.Date(string='Last Reminder Sent', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('real_estate.lease')
                    or 'New'
                )
        return super().create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = (
            self.env['ir.sequence'].next_by_code('real_estate.lease') or 'New'
        )
        return super().copy(default)

    def update_to_active(self):
        self.write({'state': 'active'})

    def update_to_draft(self):
        self.write({'state': 'draft'})

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                record.duration_month = (
                    (record.end_date - record.start_date).days // 30
                )
            else:
                record.duration_month = 0

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        today = fields.Date.today()
        for record in self:
            record.comp_is_active = bool(
                record.state == 'active'
                and record.start_date
                and record.end_date
                and record.start_date <= today <= record.end_date
            )

    @api.onchange('property_id')
    def _onchange_property_id(self):
        if self.property_id and not self.property_id.available:
            raise ValidationError('The selected property is not available.')
        if self.property_id and self.property_id.price:
            self.monthly_rent = self.property_id.price
            self.deposit_paid = self.property_id.price * 0.10

    @api.depends('start_date')
    def _compute_next_elec_recharge(self):
        for record in self:
            record.next_elec_recharge = (
                record.start_date + timedelta(days=30)
                if record.start_date else False
            )

    @api.onchange('start_date')
    def _onchange_start_date(self):
        for record in self:
            record.next_elec_recharge = (
                record.start_date + timedelta(days=30)
                if record.start_date else False
            )

    def create_maintenance_request(self):
        self.ensure_one()
        request = self.env['real_estate_p.maintenance.request'].create({
            'lease_id': self.id,
            'name': self.name,
            'issue_type': 'other',
            'description': 'Initial maintenance request',
            'scheduled_date': self.next_elec_recharge,
            'urgency': 'medium',
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

    @api.depends('main_ids.actual_cost', 'main_ids.issue_type')
    def _compute_maintenance_costs(self):
        issue_types = (
            'plumbing',
            'electrical',
            'air_condition',
            'appliance',
            'other',
        )
        for record in self:
            costs = {
                issue_type: sum(
                    record.main_ids.filtered(
                        lambda item: item.issue_type == issue_type
                    ).mapped('actual_cost')
                )
                for issue_type in issue_types
            }
            record.total_plumbing_cost = costs['plumbing']
            record.total_electrical_cost = costs['electrical']
            record.total_air_condition_cost = costs['air_condition']
            record.total_appliance_cost = costs['appliance']
            record.total_other_cost = costs['other']

    @api.model
    def _cron_auto_expire_leases(self):
        expired_leases = self.search([
            ('end_date', '<', fields.Date.today()),
            ('state', '=', 'active'),
        ])
        expired_leases.write({'state': 'expired'})

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError('End date must be after start date')

    def send_reminder_email(self):
        self.ensure_one()
        if not self.tenant_id.email:
            raise UserError('Cannot send a reminder: the tenant has no email.')

        template = self.env.ref(
            'real_estate_odoo.email_template_payment_upcoming',
            raise_if_not_found=False,
        )
        if not template:
            raise UserError('The lease payment reminder template is missing.')

        template.send_mail(self.id, force_send=True)
        self.last_reminder_sent = fields.Date.today()
        return True

    @api.model
    def cron_send_upcoming_payment_reminders(self):
        upcoming = fields.Date.today() + timedelta(days=1)
        leases = self.search([('next_payment_date', '=', upcoming)])
        for lease in leases:
            lease.send_reminder_email()
