import io
from datetime import datetime

import xlsxwriter
from odoo import http
from odoo.http import request, content_disposition


class RealEstateController(http.Controller):

    @http.route('/real_estate/property/excel_export/<int:property_id>', type='http', auth='user')
    def property_excel_export(self, property_id, **kwargs):
        property_obj = request.env['real_estate_p.property'].browse(property_id)

        if not property_obj.exists():
            return request.not_found()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Property Details')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': "#C44499",
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left'
        })

        label_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F2F2F2',
            'border': 1
        })

        data_format = workbook.add_format({'border': 1})
        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'border': 1})

        worksheet.set_column('A:A', 28)
        worksheet.set_column('B:B', 35)

        row = 0
        worksheet.merge_range(row, 0, row, 1, f'Property Report: {property_obj.name}', title_format)
        row += 2

        worksheet.merge_range(row, 0, row, 1, 'PROPERTY INFORMATION', header_format)
        row += 1

        property_data = [
            ('Property Name', property_obj.name),
            ('Property Type', dict(property_obj._fields['property_type'].selection).get(property_obj.property_type, '')),
            ('Status', 'Available' if property_obj.available else 'Occupied'),
            ('Agent', property_obj.agent_id.name or ''),
            ('Price', property_obj.price),
            ('Deposit', property_obj.deposit),
            ('Bedrooms', property_obj.bedrooms),
            ('Description', property_obj.description or ''),
        ]

        for label, value in property_data:
            worksheet.write(row, 0, label, label_format)
            if isinstance(value, float):
                worksheet.write(row, 1, value, currency_format)
            else:
                worksheet.write(row, 1, value or '', data_format)
            row += 1

        row += 2
        if property_obj.lease_ids:
            worksheet.merge_range(row, 0, row, 1, 'LEASES', header_format)
            row += 1
            worksheet.write(row, 0, 'Lease Name', header_format)
            row += 1
            for lease in property_obj.lease_ids:
                worksheet.write(row, 0, lease.name or '', data_format)
                row += 1

        workbook.close()
        output.seek(0)
        filename = f'Property_{property_obj.name.replace(" ", "_")}.xlsx'

        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )
