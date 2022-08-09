# -*- coding: utf-8 -*-
# from odoo import http


# class WebsiteEventSnippet(http.Controller):
#     @http.route('/website_event_snippet/website_event_snippet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_event_snippet/website_event_snippet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_event_snippet.listing', {
#             'root': '/website_event_snippet/website_event_snippet',
#             'objects': http.request.env['website_event_snippet.website_event_snippet'].search([]),
#         })

#     @http.route('/website_event_snippet/website_event_snippet/objects/<model("website_event_snippet.website_event_snippet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_event_snippet.object', {
#             'object': obj
#         })
