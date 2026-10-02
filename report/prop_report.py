from odoo import api, models

class PropertyReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_property_summary'
    _description = 'Property Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        properties = self.env['real_estate_p.property'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'real_estate_p.property',
            'docs': properties,
        }
