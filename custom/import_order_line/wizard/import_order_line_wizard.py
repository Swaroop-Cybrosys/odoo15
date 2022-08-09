from odoo import models, fields
import openpyxl
import base64
from io import BytesIO


class ImportOrderLine(models.TransientModel):
    _name = 'import.order.line.wizard'
    _description = 'Import Order Line'

    import_file = fields.Binary(string="Upload Xlsx File")

    def action_import(self):
        workbook = openpyxl.load_workbook(
            filename=BytesIO(base64.b64decode(self.import_file)),
            read_only=True)
        worksheet = workbook.active
        row_count = sum(
            any(col.value is not None for col in row) for max_row, row in
            enumerate(worksheet, 1))
        active_id = self.env['sale.order'].browse(self._context.get(
            'active_ids'))
        for record in worksheet.iter_rows(min_row=2, max_row=row_count,
                                          min_col=None, max_col=None,
                                          values_only=True):
            search = self.env['product.template'].search(
                [('name', '=', record[0])])
            if not search:
                res = {
                    'name': record[0],
                    'uom_id': record[3],
                    'list_price': record[4],
                    'taxes_id': None
                }
                print(res)
                product = self.env['product.product'].create(res)
                vals = {
                    'order_id': active_id.id,
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': record[2],
                    'product_uom': record[3],
                    'price_unit': record[4],
                }
                self.env['sale.order.line'].create(vals)
            else:
                vals_new = {
                    'order_id': active_id.id,
                    'product_id': self.env['product.template'].search(
                        [('name', '=', record[0])]).id,
                    'name': record[1],
                    'product_uom_qty': record[2],
                    'product_uom': record[3],
                    'price_unit': record[4],
                }
                print(vals_new)
                self.env['sale.order.line'].create(vals_new)
