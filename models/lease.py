from odoo import models, fields, api


class Lease(models.Model):
    _name = "real_estate_p.lease"
    _description = "Real Estate Lease"

    name = fields.Char(readonly=True, copy=False)
    property_id = fields.Many2one(
        'real_estate_p.property',
        string='Property',
        required=True,
    )

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

    def _cron_auto_expire_leases(self):
        """Scheduled action - expire leases whose end date has passed"""
        today = fields.Date.today()
        expired_leases = self.search([
            ('end_date', '<', today),
        ])
        for lease in expired_leases:
            lease.write({'state': 'expired'})
