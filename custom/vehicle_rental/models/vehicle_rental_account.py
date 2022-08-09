from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"
    seq = fields.Many2one('vehicle.rental.request')

    @api.constrains('payment_state')
    def _check_payment(self):
        for record in self:
            if record.payment_state == 'paid':
                record.seq.state = 'invoiced_to_request'
            else:
                pass
