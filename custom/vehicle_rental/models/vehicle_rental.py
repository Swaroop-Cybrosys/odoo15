from datetime import datetime
from odoo import models, fields, api


class VehicleRental(models.Model):
    _name = 'vehicle.rental'
    _description = 'vehicle_rental.vehicle_rental'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # FIELDS
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle",
                                 copy=False, required=True)
    name = fields.Char()
    brand = fields.Many2one(string="Brand", store=True,
                            related='vehicle_id.brand_id')
    registration_date = fields.Date('Registration Date',
                                    related='vehicle_id.reg_date', store=True,
                                    readonly=False)
    model_year = fields.Char(string="Model Year")
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                  self: self.env.user.company_id.currency_id.id)
    rent_amount = fields.Monetary()
    state = fields.Selection(
        selection=[('available', 'Available'),
                   ('not_available', 'Not Available'), ('sold', 'Sold'), ],
        string="State", default='available', required=True)
    request_count = fields.Integer(compute="_compute_request_count")
    request_ids = fields.One2many('vehicle.rental.request', 'vehicle_id',
                                  string="requests", domain=[('state', '=',
                                                              'confirmed')])
    amount_ids = fields.One2many('vehicle.rental.amount', 'rental_id')
    active = fields.Boolean(default=True)

    # FUNCTIONS
    # fetching registration year

    @api.depends('registration_date')
    def _compute_year(self):
        if self.registration_date:
            self.model_year = datetime.strptime(
                str(self.registration_date), "%Y-%m-%d").strftime('%Y')

    # concatenating name brand and model_year
    @api.onchange('registration_date')
    def _vehicle_name(self):
        if self.vehicle_id.model_id.name:
            self._compute_year()
            self.name = f'{self.vehicle_id.brand_id.name}/' \
                        f'{self.vehicle_id.model_id.name}/{self.model_year} '

    # view for smart button
    def action_rent_request(self):
        return {
            'name': 'Rent Requests',
            'domain': [('vehicle_id', '=', self.id)],
            'res_model': 'vehicle.rental.request',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'

        }

    # search_count to count marked in smart tab
    def _compute_request_count(self):
        for record in self:
            record.request_count = self.env['vehicle.rental.request'] \
                .search_count([('vehicle_id.id', '=', record.id)])
