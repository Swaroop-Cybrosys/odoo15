from odoo import http
from odoo.http import request


class MaintenanceRequest(http.Controller):
    @http.route(['/maintenance'], type='http', auth="user", website=True,
                csrf=False)
    def maintenance_request(self, **kw):
        equipments = request.env['maintenance.equipment'].sudo().search([])
        users = request.env['res.users'].sudo().search([])
        print(users)
        values = {
            'equipments': equipments,
            'users': users,
        }
        return request.render(
            "website_maintenance_request.website_maintenance_form", values,)

    @http.route('/maintenance_submit', type='http', auth='user',
                website=True, )
    def submit(self, redirect=None, **kw):
        employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        if kw:
            req = request.env['maintenance.request'].sudo().create({
                'name': kw['request_title'],
                'equipment_id': int(kw['equipment_id']),
                'description': kw['description'],
                'user_id':  int(kw['manager_id']),
                'owner_user_id': employee.id,
            })
            print(employee)
            email = request.env.ref(
                'website_maintenance_request.mail_template_maintenance_request')
            email.sudo().send_mail(req.id, force_send=True)
        return request.render(
            "website_maintenance_request.maintenance_request_success", )
