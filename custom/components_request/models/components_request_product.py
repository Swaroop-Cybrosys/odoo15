from odoo import api, models, fields


class ComponentRequestProduct(models.Model):
    _name = 'components.request.product'
    _description = 'Components Request Product'

    product_id = fields.Many2one('product.product',
                                 string="Products")
    components_request_id = fields.Many2one('components.request')
    description = fields.Char(
        string="Label", related='product_id.default_code')
    price = fields.Float(
        string="Price", related='product_id.product_tmpl_id.list_price', readonly=False)
    quantity = fields.Float(string='Quantity', default=1.0)
    sub_total = fields.Float(string='Subtotal', compute="_compute_sub_total")
    request_type = fields.Selection(
        selection=[('purchase_order', 'Purchase Order'),
                   ('internal_transfer', 'Internal Transfer')],
        string='Request Type', default='purchase_order')

    @api.depends('product_id', 'quantity', 'price')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.price * rec.quantity if rec.quantity else rec.price
