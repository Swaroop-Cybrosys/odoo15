# from odoo import api, fields, models
from random import randint

from odoo import fields, models, api, exceptions
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Estate Property"
    _rec_name = 'property_name'

    # _sql_constraints = [ ('check_percentage', 'CHECK(percentage >= 0 AND
    # percentage <= 100)', 'The percentage of an analytic distribution should
    # be between 0 and 100.') ]

    property_name = fields.Char(string="Property Name", required=True,
                                tracking=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    # date_availability = fields.Date(string="Date Availability", copy=False)
    date_availability = fields.Date(string='Date Availability',
                                    default=datetime.now() + relativedelta(
                                        months=3), copy=False)

    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default="2")
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[('east', 'East'), ('west', 'West'), ('north', 'North'),
                   ('south', 'South')], string="Garden Orientation"
    )
    active = fields.Boolean(string="Active", help="Check to make property "
                                                  "active", default=True)
    state = fields.Selection(
        selection=[('new', 'New'), ('offer_received', 'Offer Received'),
                   ('offer _accepted', 'Offer Accepted'), ('sold', 'Sold'),
                   ('cancelled', 'Cancelled')], default="new", required=True)

    # customer = fields.Many2one("res.partner", string="Customer", copy=False)
    buyer = fields.Char(string="Buyer", readonly=True)
    # to get the email of the customer
    # user_email = fields.Char('User Email', related='customer.email',
    #                          readonly=True)

    # currently logged-in user
    sales_person = fields.Many2one('res.users', string="Sales Person",
                                   default=lambda self: self.env.user)

    # user_id = fields.Many2one('res.users', string='Salesperson', index=True,
    #                       tracking=True, default=lambda self: self.env.user)

    property_type = fields.Many2one('estate.property.type',
                                    string="Property Type", copy=False)
    tag_ids = fields.Many2many('estate.property.tag',
                               string="Property Tag", copy=False)
    offer_ids = fields.One2many('estate.property.offer', 'property_id',
                                string="Offer", copy=False)
    total_area = fields.Float(compute='_compute_total',
                              string="Total Area (sqm)")

    best_price = fields.Integer(compute='_compute_best_price')

    # COMPUTATIONS
    # computing garden area + garden area
    @api.depends('living_area', 'garden_area')
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = "10"
            self.garden_orientation = "north"
        else:
            self.garden_area = "0"
            self.garden_orientation = ""
            # sample - warning message return {'warning': { 'title': _(
            # "Warning"), 'message': ('This option is not supported for
            # Authorize.net')}}

    # @api.onchange("offer_ids.price")
    # def _onchange_sellings_price(self):
    #     if self.offer_ids.status == 'accepted':
    #          self.selling_price = self.offer_ids.price
    #          print(self.offer_ids.status)
    #     else:
    #         self.selling_price = "1000"

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        self.best_price = max(self.offer_ids.mapped('price'), default=None)

    # Button Actions
    def sold_btn(self):
        if self.state == 'new':
            self.state = 'sold'
        elif self.state == 'cancelled':
            raise exceptions.UserError("Cancelled Property can't be sold")
        # else:
        #     raise exceptions.UserError('This Property is already sold.')

    def cancel_btn(self):
        if self.state == 'new':
            self.state = 'cancelled'
        elif self.state == 'sold':
            raise exceptions.UserError('Property already sold and cannot be '
                                       'cancelled.')
        # else:
        #     raise exceptions.UserError("Sold Property can't be canceled ")

    # CONSATRAINTS
    @api.constrains('expected_price')
    def _check_expected_price(self):
        for record in self:
            if record.expected_price < 0:
                raise ValidationError("Expected price cannot be negative")

    @api.constrains('selling_price')
    def _check_percentage(self):
        ninty = (self.expected_price / 100) * 90
        for record in self:
            if record.selling_price < ninty:
                raise ValidationError("Selling price cannot be less than 90 "
                                      "percent of expected price")


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _rec_name = 'property_type_name'

    property_type_name = fields.Char(string="Name", required=True)


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _rec_name = 'tag_name'
    # SQL CONSTRAINT
    _sql_constraints = [

        ('tag_name', 'UNIQUE(tag_name)',
         'Tag name must be unique ')
    ]

    tag_name = fields.Char(string="Name", required=True)

    # function for applying default color for tag
    # def _get_default_color(self):
    #     return randint(0, 7)
    #
    # color = fields.Integer(string='Color Index', default=_get_default_color)
    color = fields.Integer(string='Color')


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    # _inherit = "estate.property"
    _sql_constraints = [

        ('price_check', 'CHECK(price > 0)',
         'price must be positive ')
    ]

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'),
                                         ('refused', 'Refused')], copy=False,
                              default=False)

    partner_id = fields.Many2one('res.partner', string="Partner",
                                 required=True)
    property_id = fields.Many2one('estate.property', string="Property",
                                  required=True)

    validity = fields.Integer(string="Validity (in Days)",
                              compute="_compute_days", inverse="_date_update",
                              store=True)
    dead_line = fields.Date()

    # COMPUTATIONS
    # computing no. of days from today to selected date
    @api.depends('dead_line')
    def _compute_days(self):
        for rec in self:
            if rec.dead_line:
                start_date = date.today()
                end_date = rec.dead_line
                validity_days = (end_date - start_date).days
                if validity_days <= 0:
                    raise ValidationError('Start date should not greater than '
                                          'End date.')
                else:
                    self.validity = validity_days

    # computing the date by days + current date
    @api.onchange('validity')
    def _date_update(self):
        for record in self:
            if record.validity:
                start_date = date.today()
                no_of_days = self.validity
                record.dead_line = start_date + timedelta(days=no_of_days)
            else:
                self.dead_line = date.today() + relativedelta(days=7)

    # def action_accept(self):
    #     if self.status == False:
    #         self.status = 'accepted'
    #         self.property_id.selling_price = self.price
    #         self.property_id.customer = self.partner_id.display_name
    #         print(self.partner_id.name)
    #     # elif self.status == 'accepted':
    #     #     raise exceptions.UserError("An Offer is already accepted")
    #     elif self.status == 'refused':
    #         raise exceptions.UserError("You cannot accept a rejected offer")

    def action_accept(self):
        if self.property_id.selling_price == 0:
            self.property_id.selling_price = self.price
            self.status = 'accepted'
            self.property_id.buyer = self.partner_id.name
            # val = self.browse(cr, uid, ids)
            # for obj in val: print (obj.buyer_id.name)
            print(self.partner_id.name)
            print(self.partner_id.title)
            print(self.partner_id.display_name)
        else:
            raise exceptions.UserError("An Offer already accepted")

    def action_refuse(self):
        if self.status == False:
            self.status = 'refused'
        elif self.status == 'refused':
            raise exceptions.UserError("This Offer is already rejected")
        elif self.status == 'accepted':
            raise exceptions.UserError("You cannot reject a accepted offer")
