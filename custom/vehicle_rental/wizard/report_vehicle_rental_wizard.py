from datetime import date
import json
import io
from odoo import models, fields
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportVehicleRentalWizard(models.TransientModel):
    _name = 'report.vehicle.rental.wizard'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    vehicle_id = fields.Many2one('vehicle.rental')

    def _get_query(self):
        today = date.today()
        condition = ()
        if self.vehicle_id and self.date_start and self.date_end:

            condition = (f"t1.vehicle_id = {self.vehicle_id.id} and "
                         f"t1.from_date >= '{self.date_start}' and t1."
                         f"to_date <= '{self.date_end}'")
        elif self.date_start and self.date_end:
            condition = (
                f"t1.from_date >= '{self.date_start}' and "
                f"t1.to_date <= '{self.date_end}'")
        elif self.vehicle_id and self.date_start:
            condition = (
                f"t1.vehicle_id = {self.vehicle_id.id} and t1.from_date >= "
                f"'{self.date_start}' and t1.to_date <= '{self.date_end}'")
        elif self.vehicle_id:
            condition = (
                f" t1.vehicle_id = {self.vehicle_id.id}")
        elif self.date_start:
            print(today)
            print(self.date_start)
            condition = (
                f" t1.from_date >= '{self.date_start}' and t1.to_date <= '"
                f"{str(today)}'")
        elif self.date_end:
            condition = (
                f" t1.to_date <= "
                f"'{self.date_end}'")
        else:
            condition = ' t1.vehicle_id != 0'

        query = """
               SELECT t2.name as vehicle_name,t1.period,
               t3.name as partner_name ,t1.state
               FROM vehicle_rental_request t1 
               INNER jOIN vehicle_rental t2 
               ON t2.id = t1.vehicle_id 
               INNER JOIN res_partner t3 
               ON t3.id = t1.partner_id
               WHERE %s
               """ % condition

        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    def get_report(self):
        results = self._get_query()
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'selected_vehicle': self.vehicle_id.name,
            'results': results

        }
        return self.env.ref(
            'vehicle_rental.action_report_vehicle_report').report_action(
            self, data=data)

    def print_xlsx(self):
        results = self._get_query()
        res = {
            'start_date': self.date_start,
            'end_date': self.date_end,
            'selected_vehicle': self.vehicle_id.name,
            'results': results
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'report.vehicle.rental.wizard',
                'options': json.dumps(res, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'Excel Report',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, res, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_style = workbook.add_format({'font_size': '12px', 'bold': True})
        header = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px',
             'bg_color': '#D3D3D3'})
        txt = workbook.add_format({'font_size': '10px'})
        t_body = workbook.add_format({'font_size': '10px', 'align': 'right',
                                      'border': 1, 'border_color': 'black'})
        t_head = workbook.add_format(
            {'bold': True, 'font_color': '#fff',
             'align': 'center', 'border': 1, 'border_color': 'black'})
        bg_format = workbook.add_format({'bg_color': '#2f005b'})

        sheet.merge_range('C2:G3', 'Vehicle Rental', header)

        sheet.set_column('A:A', 13)
        sheet.set_column('B:B', 17)
        if res['selected_vehicle']:
            sheet.write('A5', 'Vehicle:', cell_style)
            sheet.write('B5', res['selected_vehicle'], txt)

        if res['start_date']:
            sheet.write('A6', 'From:', cell_style)
            sheet.write('B6', res['start_date'], txt)

        if res['end_date']:
            sheet.write('A7', 'To:', cell_style)
            sheet.write('B7', res['end_date'], txt)

        sheet.set_default_row(20)
        sheet.set_column('D:G', 17)
        sheet.conditional_format('C8:G8', {'type': 'unique',
                                           'format': bg_format})

        row = 7
        sheet.write(row, 2, 'Sl No', t_head)
        sheet.write(row, 3, 'Vehicle Name', t_head)
        sheet.write(row, 4, 'Period', t_head)
        sheet.write(row, 5, 'Partner Name', t_head)
        sheet.write(row, 6, 'State', t_head)
        sl_no = 0
        for rec in res['results']:
            row += 1
            sl_no += 1
            sheet.write(row, 2, sl_no, t_body)
            sheet.write(row, 3, rec['vehicle_name'], t_body)
            sheet.write(row, 4, rec['period'], t_body)
            sheet.write(row, 5, rec['partner_name'], t_body)
            sheet.write(row, 6, rec['state'], t_body)

        # my_dict = res['results']
        # for count, seq in enumerate(my_dict, start=1):
        #     seq.setdefault('sl_no',count)
        #     print(seq)
        # ordered_list = ["sl_no","vehicle_name", "period",
        #                 "partner_name", "state"]
        # print(ordered_list)
        # first_row = 8
        # for header in ordered_list:
        #     col = ordered_list.index(header)
        #     sheet.write(first_row, col, header)
        #
        # for row, d in enumerate(my_dict, start=10):
        #     for key, value in d.items():
        #         col = ordered_list.index(key)
        #         sheet.write(row, col, value)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
