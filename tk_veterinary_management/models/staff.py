# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalStaff(models.Model):
    _name = 'hospital.staff'
    _description = 'Registration For hospital staff employee,doctor,nurse'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', size=40, required=True)
    avatar = fields.Image(string='Image')
    related_partner_id = fields.Many2one(
        'res.partner', string='Related Partner', required=True)
    date_of_brith = fields.Date(string='Birth Date')
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female')], string='Gender')

    staff = fields.Selection(
        [('doctor', 'Doctor'), ('nurse', 'Nurse'), ('employee', 'Support Staff')], string='Staff')
    department = fields.Selection(
        [('Maintenance', 'Maintenance')], string='Department', default="Maintenance")
    bird_type = fields.Many2many('animal.type', string='Specialization')
    duration_minutes = fields.Float(string="Duration of Appointment")

    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip", size=6)

    degrees = fields.Char(string='Degrees')
    license = fields.Char(string='Licence #', size=7)
    consultancy_type = fields.Selection([('residential', 'Residential'), ('Hospital', 'Hospital')],
                                        string='Consultancy Type')

    graduation_institute = fields.Char(string='Graduation Institute')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    consultancy_charge = fields.Monetary(string='Consultancy Charges')
    # Doctor
    sunday = fields.Boolean(string="Sunday")
    monday = fields.Boolean(string="Monday")
    tuesday = fields.Boolean(string="Tuesday")
    wednesday = fields.Boolean(string="Wednesday")
    thursday = fields.Boolean(string="Thursday")
    friday = fields.Boolean(string="Friday")
    saturday = fields.Boolean(string="Saturday")
    # Relational Field Doctor
    patient_count = fields.Integer(
        string='Patient Count', compute='_compute_patient_count')
    appointment_count = fields.Integer(
        string='Appointment Count', compute='_compute_appointment_count')
    surgery_count = fields.Integer(
        string='Surgery Count', compute='_compute_surgery_count')

    today_patient_count = fields.Integer(
        string='Patient Count Today', compute="_compute_today_patient_count")
    today_surgery_count = fields.Integer(
        string='Patient Surgery Today', compute="_compute_today_surgery_count") 

    # Relational Field Nurse
    nurse_patient_count = fields.Integer(
        string='Nurse Patient Count', compute='_compute_nurse_patient_count')
    specification = fields.Char(string='Specification')
    age = fields.Char(string='Age')

    def unlink(self):
        for rec in self:
            if rec.staff == 'doctor':
                if rec.patient_count > 0 and rec.surgery_count > 0:
                    raise ValidationError(
                        _('You are not allowed to delete doctor record with having cases and surgeries'))
            return super(HospitalStaff, self).unlink()

    @api.onchange('related_partner_id')
    def related_partner_details(self):
        for rec in self:
            if rec.related_partner_id:
                rec.avatar = rec.related_partner_id.image_1920
                rec.phone = rec.related_partner_id.phone
                rec.email = rec.related_partner_id.email
                rec.street = rec.related_partner_id.street
                rec.street2 = rec.related_partner_id.street2
                rec.city = rec.related_partner_id.city
                rec.state_id = rec.related_partner_id.state_id
                rec.country_id = rec.related_partner_id.country_id
                rec.zip = rec.related_partner_id.zip

    # Depends, Onchange, Constrain
    def _compute_patient_count(self):
        for rec in self:
            patient_count = self.env['patient.case'].search_count(
                [('doctor_id', '=', rec.id)])
            rec.patient_count = patient_count
        return True
    
    def _compute_today_patient_count(self):
        today = fields.Date.today()
        tomorrow = today + timedelta(days=1)
        for rec in self:
            today_patient_count = self.env['patient.case'].sudo().search_count(
                [('state', '=', 'draft'), ('doctor_id', '=', rec.id), ('appointment_date', '>=', today),
                 ('appointment_date', '<', tomorrow)]
            )
            rec.today_patient_count = today_patient_count
        return True

    def _compute_nurse_patient_count(self):
        for rec in self:
            count = self.env['admit.patient'].search_count(
                [('nurse_id', '=', rec.id)])
            rec.nurse_patient_count = count
        return True

    def _compute_appointment_count(self):
        for rec in self:
            count = self.env['hospital.appointment'].search_count(
                [('doctor_id', '=', rec.id), ('state', '=', 'in_consultation')])
            rec.appointment_count = count
        return True

    def _compute_surgery_count(self):
        for rec in self:
            count = self.env['hospital.surgery'].search_count(
                [('doctor_id', '=', rec.id)])
            rec.surgery_count = count
        return True
    
    def _compute_today_surgery_count(self):
        today = fields.Date.today()
        tomorrow = today + timedelta(days=1)
        for rec in self:
            count = self.env['hospital.surgery'].search_count(
                [('doctor_id', '=', rec.id), ('stage', '=', 'draft'), ('schedule_date', '>=', today),
                 ('schedule_date', '<', tomorrow)])
            rec.today_surgery_count = count
        return True

    # Smart Button
    def action_view_patient(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient',
            'res_model': 'patient.case',
            'domain': [('doctor_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current'
        }
    
    def action_view_today_patient(self):
        today = fields.Date.today()
        tomorrow = today + timedelta(days=1)
        return {
            'type': 'ir.actions.act_window',
            'name': "Today's Patients",
            'res_model': 'patient.case',
            'domain': [('state', '=', 'draft'), ('doctor_id', '=', self.id), ('appointment_date', '>=', today),
                       ('appointment_date', '<', tomorrow)],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_patient_nurse(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient',
            'res_model': 'admit.patient',
            'domain': [('nurse_id', '=', self.id)],
            'context': {'default_nurse_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_appointment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment',
            'res_model': 'hospital.appointment',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id},
            'view_mode': 'calendar,tree,form',
            'target': 'current'
        }

    def action_view_surgeries(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Surgeries',
            'res_model': 'hospital.surgery',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id},
            'view_mode': 'calendar,tree,form',
            'target': 'current'
        }

    def action_view_today_surgeries(self):
        today = fields.Date.today()
        tomorrow = today + timedelta(days=1)
        return {
            'type': 'ir.actions.act_window',
            'name': "Today's Surgeries",
            'res_model': 'hospital.surgery',
            'domain': [('doctor_id', '=', self.id), ('stage', '=', 'draft'), ('schedule_date', '>=', today),
                       ('schedule_date', '<', tomorrow)],
            'context': {'default_doctor_id': self.id},
            'view_mode': 'calendar,tree,form',
            'target': 'current'
        }