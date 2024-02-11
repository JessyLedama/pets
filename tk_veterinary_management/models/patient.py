# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import calendar
from datetime import date
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient'
    _rec_name = 'patient_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Patient
    patient_sequence_number = fields.Char(
        string='Sequence', copy=False, readonly=True, default=lambda self: 'New')
    patient_name = fields.Char(required=True, size=40)
    bird_type = fields.Many2one('animal.type', string='Pet Type')
    bird = fields.Char(string='Breed', required=True, size=40)
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female')], string='Gender', required=True)
    avatar = fields.Binary(string="Image")
    age = fields.Integer(string='Age')
    age_type = fields.Selection(
        [('Days', 'Days'), ('Months', 'Months'), ('Years', 'Years')])
    id_number = fields.Char(string='Id Number', required=True, size=40)
    company_id = fields.Many2one(
        'res.company', string='Company', index=True, default=lambda self: self.env.company)

    # Other Fields
    stages = fields.Selection([('Draft', 'Draft'), ('Active', 'Active'), ('done', 'Close')], string='Stages',
                              default='Draft')
    contact_id = fields.Many2one(
        'res.partner', string='Contact', domain="[('is_patient','=','True')]")
    contact_state = fields.Boolean(string='Contact State')

    # Owner
    customer_id = fields.Many2one("res.partner", string="Name", required=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip", size=6)

    # One2many
    disease_ids = fields.One2many(
        'hospital.disease', 'patient_id', string='Disease')
    vaccination_ids = fields.One2many(
        'hospital.vaccination.details', 'patient_id', string='Vaccination Details')
    case_ids = fields.One2many('patient.case', 'patient_id', string='Cases')
    appointment_ids = fields.One2many(
        'hospital.appointment', 'patient_id', string='Appointment')

    # Count
    procedures_count = fields.Integer(
        string='Procedures Count', compute='_compute_procedures_count')
    grooming_count = fields.Integer(
        string='Grooming Count', compute='_compute_grooming_count')
    training_count = fields.Integer(
        string='Training Count', compute='_compute_training_count')
    cases_count = fields.Integer(
        string='Case Count', compute='_compute_case_count')
    surgery_count = fields.Integer(
        string='Appointment Count', compute='_compute_surgery_count')
    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')
    patient_report_count = fields.Integer(
        string='Report Count', compute='_compute_report_count')
    invoice_count = fields.Integer(
        string='Invoice Count', compute='_compute_invoice_count')

    # General
    width = fields.Char(string='Width')
    height = fields.Char(string='Height')
    color = fields.Char(string='Color')
    weight = fields.Float(string='Weight')
    blood_type = fields.Char(string='Blood Type')
    rh = fields.Char(string='RH')
    behaviour = fields.Char(string='Behaviour', required=True)

    # Extra Field
    insurance = fields.Char(string='Insurance')
    nurse_id = fields.Many2one(
        'hospital.staff', string='Nurse', domain="[('staff','=','nurse')]")
    service_id = fields.Many2one('service.type', 'Service Types')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_sequence_number', 'New') == 'New':
                vals['patient_sequence_number'] = self.env['ir.sequence'].next_by_code(
                    'rest.seq.patient') or 'New'
        res = super(Patient, self).create(vals_list)
        return res

    def unlink(self):
        for rec in self:
            if rec.invoice_count > 0:
                raise ValidationError(
                    _("You are not allowed to delete patients with invoices"))
            return super(Patient, self).unlink()

    @api.onchange('customer_id')
    def customer_details(self):
        for rec in self:
            if rec.customer_id:
                rec.phone = rec.customer_id.phone
                rec.email = rec.customer_id.email
                rec.street = rec.customer_id.street
                rec.street2 = rec.customer_id.street2
                rec.city = rec.customer_id.city
                rec.state_id = rec.customer_id.state_id
                rec.country_id = rec.customer_id.country_id
                rec.zip = rec.customer_id.zip

    @api.depends('case_ids')
    def _compute_procedures_count(self):
        for rec in self:
            rec.procedures_count = self.env['patient.case'].search_count(
                [('patient_id', '=', rec.id)])
        return True

    @api.depends('case_ids')
    def _compute_grooming_count(self):
        for rec in self:
            rec.grooming_count = self.env['grooming.details'].search_count(
                [('patient_id', '=', rec.id)])
        return True

    @api.depends('case_ids')
    def _compute_training_count(self):
        for rec in self:
            rec.training_count = self.env['training.details'].search_count(
                [('patient_id', '=', rec.id)])
        return True

    def action_procedures_case(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Procedure',
            'res_model': 'patient.case',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_grooming(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Grooming',
            'res_model': 'grooming.details',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_training(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Training',
            'res_model': 'training.details',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def draft_to_confirm(self):
        self.stages = 'Active'

    def confirm_to_done(self):
        self.stages = 'done'

    def done_to_draft(self):
        self.stages = 'Draft'

    @api.depends('case_ids')
    def _compute_case_count(self):
        for rec in self:
            case_count = self.env['hospital.appointment'].search_count(
                [('patient_id', '=', rec.id)])
            rec.cases_count = case_count
        return True

    def action_patient_case(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment',
            'res_model': 'hospital.appointment',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    @api.depends('case_ids')
    def _compute_surgery_count(self):
        for rec in self:
            case_ids = self.env['patient.case'].search(
                [('patient_id', '=', rec.id)]).mapped('id')
            count = self.env['hospital.surgery'].search_count(
                [('case_id', 'in', case_ids)])
            rec.surgery_count = count
        return True

    @api.depends('case_ids')
    def _compute_prescription_count(self):
        for rec in self:
            case_ids = self.env['patient.case'].search(
                [('patient_id', '=', rec.id)]).mapped('id')
            cases_count = self.env['hospital.prescription'].search_count(
                [('case_id', 'in', case_ids)])
            rec.prescription_count = cases_count
        return True

    @api.depends('case_ids')
    def _compute_report_count(self):
        for rec in self:
            case_ids = self.env['patient.case'].search(
                [('patient_id', '=', rec.id)]).mapped('id')
            report_count = self.env['patient.report'].search_count(
                [('case_id', 'in', case_ids)])
            rec.patient_report_count = report_count
        return True

    def action_view_surgery(self):
        case_ids = self.env['patient.case'].search(
            [('patient_id', '=', self.id)]).mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Surgery',
            'res_model': 'hospital.surgery',
            'domain': [('case_id', 'in', case_ids)],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_patient_report_count(self):
        case_ids = self.env['patient.case'].search(
            [('patient_id', '=', self.id)]).mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report',
            'res_model': 'patient.report',
            'domain': [('case_id', 'in', case_ids)],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_prescription_appointment(self):
        case_ids = self.env['patient.case'].search(
            [('patient_id', '=', self.id)]).mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescription',
            'res_model': 'hospital.prescription',
            'domain': [('case_id', 'in', case_ids)],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Case',
            'res_model': 'account.move',
            'domain': [('partner_id', '=', self.customer_id.id), ('move_type', '=', 'out_invoice')],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    @api.depends('case_ids')
    def _compute_invoice_count(self):
        for rec in self:
            invoice_count = self.env['account.move'].search_count(
                [('partner_id', '=', self.customer_id.id), ('move_type', '=', 'out_invoice')])
            rec.invoice_count = invoice_count
        return True

    @api.model
    def get_hospital_stats(self):
        domain = [('state', '=', 'in_consultation')]
        today_date = fields.Date.today()
        day = (today_date.strftime('%A')).lower()
        active_grooming = self.env['grooming.details'].search_count(domain)
        active_training = self.env['training.details'].search_count(domain)
        active_procedure = self.env['patient.case'].search_count(domain)
        maintain_count = self.env['hospital.maintenance'].search_count(
            [('stages', '=', 'draft')])
        doctor = self.env['hospital.staff'].search_count(
            [('staff', '=', 'doctor')])
        nurse = self.env['hospital.staff'].search_count(
            [('staff', '=', 'nurse')])
        surgery = self.env["hospital.surgery"].search_count([])

        today_grooming_count = sum(1 for data in self.env['grooming.details'].search(domain) if
                                   data.appointment_date and data.appointment_date.date() == today_date)
        today_procedure_count = sum(1 for data in self.env['patient.case'].search(domain) if
                                    data.appointment_date and data.appointment_date.date() == today_date)
        today_training_count = sum(1 for data in self.env['training.details'].search(domain) if
                                   data.appointment_date and data.appointment_date.date() == today_date)
        today_surgery_count = sum(
            1 for data in self.env['hospital.surgery'].search([]) if data.schedule_date.date() == today_date)
        doctor_day = self.env['hospital.staff'].search_count(
            [(day, '=', True), ('staff', '=', 'doctor')])
        nurse_day = self.env['hospital.staff'].search_count(
            [(day, '=', True), ('staff', '=', 'nurse')])

        # Extra
        mon_appointment_details = [self.procedures_month_appointment(), self.grooming_month(),
                                   self.training_month()]
        active_appointment_date = [self.appointment_date(), self.appointment_procedures(), self.appointment_grooming(),
                                   self.appointment_training()]
        invoice = [self.get_month_invoice_key(), self.get_month_invoice()]
        return {
            'active_grooming': active_grooming,
            'active_training': active_training,
            'active_procedure': active_procedure,
            'maintain_count': maintain_count,
            'doctor': doctor,
            'nurse': nurse,
            'surgery': surgery,
            'today_grooming_count': today_grooming_count,
            'today_procedure_count': today_procedure_count,
            'today_training_count': today_training_count,
            'today_surgery_count': today_surgery_count,
            'doctor_day': doctor_day,
            'nurse_day': nurse_day,
            'months_appointment_details': mon_appointment_details,
            'active_appointment_date': active_appointment_date,
            'grooming_product': self.get_to_grooming_product(),
            'medicine_product': self.get_medicine_product(),
            'invoice': invoice,
        }

    def get_month_invoice(self):
        year = fields.date.today().year
        bill_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        bill = self.env['account.move'].search([])
        for data in bill:
            if data.invoice_date:
                if data.invoice_date.year == year:
                    bill_dict[data.invoice_date.strftime("%B")] = bill_dict[data.invoice_date.strftime(
                        "%B")] + data.amount_total
        return list(bill_dict.values())

    def get_month_invoice_key(self):
        year = fields.date.today().year
        bill_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        bill = self.env['account.move'].search([])
        for data in bill:
            if data.invoice_date and data.invoice_date.year == year:
                bill_dict[data.invoice_date.strftime("%B")] = bill_dict[
                    data.invoice_date.strftime("%B")] + data.amount_total
        return list(bill_dict.keys())

    def get_to_grooming_product(self):
        product, qty, data = [], [], []
        product_template = self.env['product.template'].search(
            [('is_grooming_product', '=', True)]).mapped('id')
        product_product = self.env['product.product'].search(
            [('product_tmpl_id', 'in', product_template)]).mapped('id')
        for group in self.env['account.move.line'].read_group([('product_id', 'in', product_product)],
                                                              ['quantity',
                                                                  'product_id'],
                                                              ['product_id'],
                                                              orderby="quantity DESC", limit=10):
            if group['product_id']:
                name = self.env['product.product'].sudo().browse(
                    int(group['product_id'][0])).name
                product.append(name)
                qty.append(group['quantity'])
        data = [product, qty]
        return data

    def get_medicine_product(self):
        product, qty, data = [], [], []
        product_template = self.env['product.template'].search(
            [('is_medicine', '=', True)]).mapped('id')
        product_product = self.env['product.product'].search(
            [('product_tmpl_id', 'in', product_template)]).mapped('id')
        for group in self.env['account.move.line'].read_group([('product_id', 'in', product_product)],
                                                              ['quantity',
                                                                  'product_id'],
                                                              ['product_id'],
                                                              orderby="quantity DESC", limit=10):
            if group['product_id']:
                name = self.env['product.product'].sudo().browse(
                    int(group['product_id'][0])).name
                product.append(name)
                qty.append(group['quantity'])
        data = [product, qty]
        return data

    def appointment_date(self):
        day_dict = {}
        year = fields.date.today().year
        month = fields.date.today().month
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, num_days + 1)]
        for data in days:
            day_dict[data.strftime('%d') + " " + data.strftime('%h')] = 0
        return list(day_dict.keys())

    def appointment_procedures(self):
        day_dict = {}
        year = fields.date.today().year
        month = fields.date.today().month
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, num_days + 1)]
        for data in days:
            day_dict[data.strftime('%d') + " " + data.strftime('%h')] = 0
        booking = self.env['patient.case'].search(
            [('state', 'not in', ['draft', 'cancel']), ('appointment_date', '!=', False)])
        for data in booking:
            if data.appointment_date.year == year and month == data.appointment_date.month:
                booking_time = data.appointment_date.strftime(
                    '%d') + " " + data.appointment_date.strftime('%h')
                day_dict[booking_time] = day_dict[booking_time] + 1
        return list(day_dict.values())

    def appointment_grooming(self):
        day_dict = {}
        year = fields.date.today().year
        month = fields.date.today().month
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, num_days + 1)]
        for data in days:
            day_dict[data.strftime('%d') + " " + data.strftime('%h')] = 0
        booking = self.env['grooming.details'].search(
            [('state', 'not in', ['draft', 'cancel']), ('appointment_date', '!=', False)])
        for data in booking:
            if data.appointment_date.year == year and month == data.appointment_date.month:
                booking_time = data.appointment_date.strftime(
                    '%d') + " " + data.appointment_date.strftime('%h')
                day_dict[booking_time] = day_dict[booking_time] + 1

        return list(day_dict.values())

    def appointment_training(self):
        day_dict = {}
        year = fields.date.today().year
        month = fields.date.today().month
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, num_days + 1)]
        for data in days:
            day_dict[data.strftime('%d') + " " + data.strftime('%h')] = 0
        booking = self.env['training.details'].search(
            [('state', 'not in', ['draft', 'cancel']), ('appointment_date', '!=', False)])
        for data in booking:
            if data.appointment_date.year == year and month == data.appointment_date.month:
                booking_time = data.appointment_date.strftime(
                    '%d') + " " + data.appointment_date.strftime('%h')
                day_dict[booking_time] = day_dict[booking_time] + 1

        return list(day_dict.values())

    def procedures_month_appointment(self):
        data_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        procedures_month = self.env['patient.case'].search(
            [('state', 'not in', ['draft', 'cancel']), ('appointment_date', '!=', False)])
        for data in procedures_month:
            data_dict[data.appointment_date.strftime(
                "%B")] = data_dict[data.appointment_date.strftime("%B")] + 1
        return list(data_dict.values())

    def grooming_month(self):
        data_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        grooming_month = self.env['grooming.details'].search(
            [('state', 'not in', ['draft', 'cancel']), ('appointment_date', '!=', False)])
        for data in grooming_month:
            data_dict[data.appointment_date.strftime(
                "%B")] = data_dict[data.appointment_date.strftime("%B")] + 1
        return list(data_dict.values())

    def training_month(self):
        data_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        training_month = self.env['training.details'].search(
            [('state', 'not in', ['draft', 'cancel']), ('appointment_date', '!=', False)])
        for data in training_month:
            data_dict[data.appointment_date.strftime(
                "%B")] = data_dict[data.appointment_date.strftime("%B")] + 1
        return list(data_dict.values())


class ContactPatient(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean()
    patient_id = fields.Many2one('hospital.patient', string='Patient')
