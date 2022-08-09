from odoo import models, fields
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Integer(string="Discount Amount")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.discount_amount = sum(self.order_line.mapped('price_unit')) \
                               - sum(self.order_line.mapped('price_subtotal'))

        discount_sum = sum(
            self.env['sale.order'].search([]).mapped('discount_amount'))
        monthly_limit = float(self.env['ir.config_parameter'].sudo().get_param(
            'sale.monthly_discount_limit'))
        self.discount_check()

    def discount_check(self):
        discount_sum = float(sum(
            self.env['sale.order'].search([]).mapped('discount_amount')))
        monthly_limit = float(self.env['ir.config_parameter'].sudo().get_param(
            'sale.monthly_discount_limit'))
        for line in self.order_line:
            if line.discount and monthly_limit < discount_sum:
                raise ValidationError(
                    f'Monthly Limit of ₹ {monthly_limit} is used up.\n '
                    f'Total amount used is  = {discount_sum} ')

    def clear_discount_amount(self):
        self.env.cr.execute("""UPDATE sale_order SET discount_amount=0 """)
