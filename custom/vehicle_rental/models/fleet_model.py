from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    reg_date = fields.Date(string="Registration Date")
