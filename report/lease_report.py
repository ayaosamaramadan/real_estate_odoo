from odoo import api, models


class LeaseReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_lease_summary'
    _description = 'Lease Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        leases = self.env['real_estate_p.lease'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'real_estate_p.lease',
            'docs': leases,
        }
