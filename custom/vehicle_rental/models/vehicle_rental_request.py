from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import Command


class VehicleRentalRequest(models.Model):
    _name = 'vehicle.rental.request'
    _description = 'Vehicle Rental Request'
    _inherit = ["mail.thread", "mail.activity.mixin", ]
    _rec_name = 'sequence'

    # FIELDS
    sequence = fields.Char(string="Reference No:", readonly=True,
                           required=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', required=True)
    mail = fields.Char('email', related='partner_id.email')
    request_date = fields.Date(default=datetime.today())
    vehicle_id = fields.Many2one('vehicle.rental', required=True)
    from_date = fields.Date(default=date.today(), string="From Date")
    to_date = fields.Date(string="To Date")
    period = fields.Text(
        string="period", compute="_compute_period", store=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirmed', 'Confirmed'),
                                        ('invoiced_to_request',
                                         'Invoiced to request'),
                                        ('returned', 'Returned')],
                             default='draft')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    rent = fields.Monetary(string="Rent", compute="_compute_rent", store=True)
    period_type = fields.Selection(selection=[('hour', 'Hours'),
                                              ('day', 'Days'),
                                              ('week', 'Weeks'),
                                              ('month', 'Months'), ])

    rental_amount_id = fields.Many2one('vehicle.rental.amount')
    warning = fields.Boolean(default=False)
    late = fields.Boolean(default=False)
    invoice_count = fields.Integer(compute="_compute_invoice_count",
                                   string=' Invoice Count', copy=False,
                                   store=True)
    invoice_ids = fields.Many2many(
        'account.move', string='Rental Invoices', copy=False, store=True)
    account_move_id = fields.Many2one(
        'account.move', string='Rental counts', copy=False, store=True)

    # late date check
    def late_return(self):
        for rec in self.env['vehicle.rental.request'].search(
                [('state', '=', 'confirmed')]):
            result = (rec.to_date - date.today()).days
            if result == 2:
                rec.write({'warning': True})
                rec.write({'late': False})
            elif result < 0:
                rec.write({'late': True})
                rec.write({'warning': False})
            else:
                rec.write({'warning': False})
                rec.write({'late': False})

    # creating sequence no
    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'vehicle.rental.request')
        return super(VehicleRentalRequest, self).create(vals)

    # Confirm button action
    def confirm_btn(self):
        if self.state == 'draft':
            self.state = 'confirmed'
            self.vehicle_id.state = 'not_available'

    # computing invoice count
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('ref', '=', self.sequence)])

    def create_invoice_btn(self):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id,
            'ref': self.sequence,
            'seq': self,
            'invoice_user_id': self.env.user.id,
            'invoice_date': date.today(),
            'invoice_line_ids': [
                Command.create({
                    "name": self.vehicle_id.name,
                    "price_unit": self.rent,
                    "quantity": 1,
                })
            ],
        })
        self._compute_invoice_count()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            'res_id': invoice.id,
            "domain": [('id', 'in', invoice.invoice_line_ids.move_id.ids)],
            "context": {"create": False},
            'view_mode': 'form'
        }

    def action_view_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rental Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('move_type', '=', 'out_invoice'),
                       ('ref', '=', self.sequence)],
            'context': "{'create': False}"
        }

    def return_btn(self):
        if self.state == 'invoiced_to_request':
            self.state = 'returned'
            self.vehicle_id.state = 'available'

    # computation on no of days between two dates computation
    @api.depends('to_date', 'from_date')
    def _compute_period(self):
        if self.to_date:
            period_days = (self.to_date - self.from_date).days
            if period_days <= 0:
                raise ValidationError('Start date should not greater than '
                                      'End date.')
            else:
                self.period = f'{period_days} days'

    # fetching rent amount from vehicle.rental model
    @api.onchange('vehicle_id')
    def _get_rent(self):
        self.rent = self.vehicle_id.rent_amount

    @api.depends('period_type', 'to_date', 'from_date')
    def _compute_rent(self):

        for record in self.env['vehicle.rental.amount'].search(
                [('rental_id.id', '=', self.vehicle_id.id), ('time', '=', self.period_type)]):

            rec = record.amount
            difference_in_days = self.to_date - self.from_date

            if self.period_type == 'hour':
                self.period = f'{difference_in_days.total_seconds() / 3600} Hours'
                self.rent = (difference_in_days.total_seconds() / 3600) * rec

            elif self.period_type == 'day':
                self.period = f'{difference_in_days.days} Days'
                self.rent = difference_in_days.days * rec

            elif self.period_type == 'week':
                difference_in_weeks = int(difference_in_days.days / 7)
                if difference_in_weeks == 0:
                    raise ValidationError(
                        f'Time period between selected dates is {difference_in_days.days} days. Please choose the correct time period')
                else:
                    self.period = f'{difference_in_weeks} Week'
                    self.rent = difference_in_weeks * rec
            elif self.period_type == 'month':
                difference_in_months = self.to_date.month - self.from_date.month
                if difference_in_months == 0:
                    raise ValidationError(
                        f'Time period between selected dates is {difference_in_days.days} days. Please choose the correct time period')
                else:
                    self.period = f'{difference_in_months} Months'
                    self.rent = difference_in_months * rec
