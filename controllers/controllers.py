# -*- coding: utf-8 -*-
# from odoo import http


# class RealEstateP(http.Controller):
#     @http.route('/real_estate_p/real_estate_p', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/real_estate_p/real_estate_p/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('real_estate_p.listing', {
#             'root': '/real_estate_p/real_estate_p',
#             'objects': http.request.env['real_estate_p.real_estate_p'].search([]),
#         })

#     @http.route('/real_estate_p/real_estate_p/objects/<model("real_estate_p.real_estate_p"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('real_estate_p.object', {
#             'object': obj
#         })

