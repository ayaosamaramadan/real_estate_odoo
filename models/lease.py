from odoo import models, fields, api


class Lease(models.Model):
    _name = "real_estate_p.lease"
    _description = "Real Estate Lease"

    name = fields.Char(required=True)
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