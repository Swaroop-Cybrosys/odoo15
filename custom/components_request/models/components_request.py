from datetime import date
from odoo import models, fields, api


class ComponentsRequest(models.Model):
    _name = 'components.request'
    _description = 'Components Request'
    _rec_name = 'reference'

    def _get_employee(self):
        return self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)]).id

    reference = fields.Char(string="reference", default="New", readonly=True)
    employee_id = fields.Many2one('hr.employee', default=_get_employee,
                                  string="Employee",
                                  )
    components_request_ids = fields.One2many(
        'components.request.product', 'components_request_id')
    total_amount = fields.Float(
        compute='_compute_total_amount', string='Total')
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('waiting_for_approval', 'Waiting For Approval'),
                   ('second_approval', 'Second Approval'),
                   ('approved', 'Approved'),
                   ('rejected', 'Rejected')], default='draft')
    toggle_moves_btn = fields.Boolean(default=False)
    hide_approve_btn = fields.Boolean(default=True)
    po_count = fields.Integer(compute="_compute_po_count")
    int_count = fields.Char(string="Internal Transfer")

    @api.depends('components_request_ids.sub_total')
    def _compute_total_amount(self):
        self.total_amount = sum(
            self.components_request_ids.mapped('sub_total'))

    def send_to_manager(self):
        self.state = 'waiting_for_approval'

    def head_approve_btn(self):
        self.toggle_moves_btn = True
        self.hide_approve_btn = False

    def reject_btn(self):
        self.state = 'rejected'

    def manager_approve_btn(self):
        self.state = 'second_approval'

    # creating sequence no
    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code(
            'components.request')
        return super(ComponentsRequest, self).create(vals)

    def _compute_po_count(self):
        for record in self:
            record.po_count = self.env['purchase.order'].search_count(
                [('components_req_id', '=', self.id)])

    def action_view_po(self):
        return {
            "name": 'Component Request RFQs',
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "domain": [('components_req_id', '=', self.id)],
            "context": {"create": False},
            "view_mode": 'tree,form'
        }

    def action_view_int(self):
        return {
            "name": 'Component Request Transfers',
            "type": "ir.actions.act_window",
            "res_model": 'stock.picking',
            "domain": [('origin', '=', self.reference)],
            "context": {"create": False},
            "view_mode": 'tree,form'
        }

    def generate_moves(self):
        rec = self.components_request_ids
        self.state = 'approved'
        for line in rec:
            if line.request_type == 'purchase_order':
                partner = line.product_id.product_tmpl_id.seller_ids.filtered(
                    lambda l: l.name).sorted(key=lambda s: s.price)

                po_list = [(0, 0, {
                    'product_id': line.product_id.id,
                    "price_unit": partner[0].price,
                    'product_qty': line.quantity
                })]
                purchase_orders = self.env['purchase.order'].create(
                    {'partner_id': partner[0].name.id,
                     'state': 'sent',
                     'origin': self.reference,
                     'date_planned': date.today(),
                     'order_line': po_list,
                     'components_req_id': self.id
                     })
                print(purchase_orders.components_req_id)

            elif line.request_type == 'internal_transfer':
                pick_line_values = {
                    "product_id": line.product_id.id,
                    "name": line.product_id.description,
                    "product_uom_qty": line.quantity,
                    "product_uom": 1,
                    'location_id': 8,
                    'location_dest_id': 8,

                }
                pick_lines = [(0, 0, pick_line_values)]
                picking = {

                    'location_id': 8,
                    'location_dest_id': 8,
                    'move_type': 'direct',
                    'picking_type_id': 5,
                    'move_lines': pick_lines,
                    'origin': self.reference,
                }
                transfer = self.env['stock.picking'].create(picking)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    components_req_id = fields.Many2one('components.request')
