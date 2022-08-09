from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def import_btn(self):
        return {
            'name': 'Import File',
            'domain': [],
            'res_model': 'import.order.line.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'new',
        }
