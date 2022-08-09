from odoo import models, fields


class VehicleRentalAmount(models.Model):
    _name = 'vehicle.rental.amount'

    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                  self: self.env.user.company_id.currency_id.id)
    time = fields.Selection(selection=[('hour', 'Hour'),
                                       ('day', 'Days'),
                                       ('week', 'Week'),
                                       ('month', 'Month')])
    amount = fields.Monetary(store=True, copy=False)

    rental_id = fields.Many2one('vehicle.rental')
