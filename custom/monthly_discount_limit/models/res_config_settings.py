from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    monthly_discount_limit = fields.Monetary(string="Monthly Discount Limit",
                                             currency_field='company_currency_id',
                                             readonly=False)
    company_currency_id = fields.Many2one('res.currency',
                                          related='company_id.currency_id',
                                          string="Company Currency",
                                          readonly=True)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'sale.monthly_discount_limit', self.monthly_discount_limit)
        return res

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        monthly_limit = self.env['ir.config_parameter'].sudo().get_param(
            'sale.monthly_discount_limit')
        res.update(
            monthly_discount_limit=float(monthly_limit)
        )
        return res

    def test_btn(self):
        self.env.cr.execute("""UPDATE sale_order SET discount_amount=0 """)
