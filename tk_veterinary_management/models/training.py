# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AnimalTraining(models.Model):
    _name = 'training.details'
    _description = 'Training Details'
    _rec_name = 'training_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    training_no = fields.Char(string='Sequence', readonly=True, copy=False, index=True,
                              default=lambda self: 'New')
    appointment_id = fields.Many2one('hospital.appointment',
                                     domain="[('state','=','in_consultation'),('service_type','=','Training')]",
                                     string='Appointment')
    patient_id = fields.Many2one('hospital.patient', string='Animal')
    bird_type = fields.Many2one(
        'animal.type', string='Animal Type', related="patient_id.bird_type")
    bird = fields.Char(string='Breed', related="patient_id.bird")
    certificate_no = fields.Char(string="Certificate No")
    package_id = fields.Many2one(
        'training.type', string='Package', domain="[('bird_type', '=', bird_type)]", )
    appointment_date = fields.Datetime(string="Appointment Date")
    animal = fields.Char(
        related="appointment_id.patient_name", string="Animal ")
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    charges = fields.Monetary(
        related='package_id.charges', string='Charge', store=True)
    package_days = fields.Integer(
        related='package_id.days', store=True, string="Package Duration")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', compute="compute_end_date")
    days = fields.Integer(string="Total Days")
    state = fields.Selection([('draft', 'Draft'),
                              ('in_consultation', 'In Progress'),
                              ('complete', 'Complete'),
                              ('cancel', 'Cancel')],
                             string='State', default='draft', required=True)
    invoice_id = fields.Many2one('account.move', string='Invoice')
    signature = fields.Binary(string="Signature")
    training_emp_ids = fields.Many2many(
        "res.users", compute="_get_training_employees")
    training_employee_id = fields.Many2one('res.users', string="Training Employee",
                                           domain="[('id','in',training_emp_ids)]")

    is_invoice_created = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('training_no', 'New') == 'New':
                vals['training_no'] = self.env['ir.sequence'].next_by_code(
                    'training.details') or 'New'
        res = super(AnimalTraining, self).create(vals_list)
        return res

    def unlink(self):
        for rec in self:
            if rec.state in ['complete', 'in_consultation']:
                raise ValidationError(
                    _("You are not allowed to delete an appointment in the consultation or close state."))
            return super(AnimalTraining, self).unlink()

    @api.depends("training_employee_id")
    def _get_training_employees(self):
        for rec in self:
            emp_ids = []
            recs = self.env["res.users"].sudo().search([])
            for data in recs:
                if data.has_group("tk_veterinary_management.veterinary_training_employee"):
                    emp_ids.append(data.id)
            rec.training_emp_ids = emp_ids

    def action_confirm_appointment(self):
        self.state = 'in_consultation'

    def action_cancel_appointment(self):
        self.state = 'cancel'

    def complete(self):
        self.state = 'complete'

    def action_invoices(self):
        invoice_id = self.env['account.move'].sudo().create({
            'partner_id': self.patient_id.customer_id.id,
            'invoice_date': fields.Date.today(),
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref('tk_veterinary_management.training_product_1').id,
                'name': 'Training Service',
                'quantity': 1,
                'price_unit': self.charges
            })],
        })
        self.invoice_id = invoice_id.id
        # self.state = 'complete'
        self.is_invoice_created = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_complete_appointment(self):
        if self.invoice_id.payment_state == "paid":
            self.state = "complete"
        else:
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Invoice Payment Pending'),
                    'type': 'warning',
                    'message': _('You cannot close the appointment until the invoice is paid.'),
                    'sticky': False,
                }
            }
            return notification

    @api.depends('start_date', 'package_days')
    def compute_end_date(self):
        for rec in self:
            end_date = False
            if rec.start_date:
                end_date = rec.start_date + \
                    relativedelta(days=rec.package_days)
            rec.end_date = end_date


class TrainingType(models.Model):
    _name = 'training.type'
    _description = ' Training Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Package Name', required=True)
    bird_type = fields.Many2one('animal.type', string='Pet Type')
    service_type = fields.Selection([('home', 'At Home'), ('center', 'At Center')], string='Service Type',
                                    required=True)
    days = fields.Integer(string='Days')
    charges = fields.Monetary(string='Charge')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    inclusion_ids = fields.Many2many('training.inclusion', string="Inclusion")
    exclusion_ids = fields.Many2many('training.exclusion', string="Exclusion")


class TrainingInclusion(models.Model):
    _name = 'training.inclusion'
    _description = "Training Inclusion"

    name = fields.Char(string="Title")
    color = fields.Integer(string='Color')


class TrainingExclusion(models.Model):
    _name = 'training.exclusion'
    _description = "Training Exclusion"

    name = fields.Char(string="Title")
    color = fields.Integer(string='Color')
