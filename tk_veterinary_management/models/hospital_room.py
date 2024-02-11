# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class HospitalRoom(models.Model):
    _name = 'hospital.room'
    _description = 'Room Management for Animal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'room_no'

    room_no = fields.Char(string='Room No.', required=True, )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    charge = fields.Monetary(string='Charges', store=True, required=True)
    stage = fields.Selection([('free', 'Available'),
                              ('maintenance', 'Maintenance')], string='Stage', default='free', required=True)
    bed_ids = fields.One2many('hospital.bed', 'room_id', string='Table', required=True)
    capacity = fields.Integer(string='Table Capacity', compute='get_capacity_bed_count')
    booked_bed = fields.Integer(string='Allocated Table', compute='get_booked_bed_count')
    available_bed = fields.Integer(string='Available Table', compute='get_available_bed_count')

    def action_free(self):
        for rec in self:
            rec.stage = 'free'
        return True

    def action_maintenance(self):
        for rec in self:
            rec.stage = 'maintenance'
        return True

    def get_capacity_bed_count(self):
        count = self.env['hospital.bed'].search_count([('room_id', '=', self.id)])
        self.capacity = count

    def get_available_bed_count(self):
        count = self.env['hospital.bed'].search_count([('room_id', '=', self.id), ('stage', '=', 'free')])
        self.available_bed = count

    def get_booked_bed_count(self):
        count = self.env['hospital.bed'].search_count([('room_id', '=', self.id), ('stage', '=', 'book')])
        self.booked_bed = count

    def total_capacity_bed_views(self):
        return {
            'name': 'Tables',
            'domain': [('room_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hospital.bed',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': "ir.actions.act_window"
        }

    #
    def available_bed_views(self):
        return {
            'name': 'Tables',
            'domain': [('room_id', '=', self.id), ('stage', '=', 'free')],
            'view_type': 'form',
            'res_model': 'hospital.bed',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': "ir.actions.act_window"
        }

    def allocated_bed_views(self):
        return {
            'name': 'Tables',
            'domain': [('room_id', '=', self.id), ('stage', '=', 'book')],
            'view_type': 'form',
            'res_model': 'hospital.bed',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': "ir.actions.act_window"
        }


class HospitalBed(models.Model):
    _name = 'hospital.bed'
    _description = 'Table Management for Animal'
    _rec_name = 'bed_no'

    bed_no = fields.Char(string='Table No.', required=True)
    room_id = fields.Many2one('hospital.room')
    stage = fields.Selection([('free', 'Available'), ('book', 'Booked')], string='Stage', default='free', required=True)

    def action_free(self):
        for rec in self:
            rec.stage = 'free'
        return True

    def action_book(self):
        for rec in self:
            rec.stage = 'book'
        return True


class HospitalAdmitPatient(models.Model):
    _name = 'admit.patient'
    _description = 'Admit Patient Management'
    _rec_name = 'case_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    seq_no = fields.Char(string='Admit Patient-No', readonly=True, copy=False, index=True, default=lambda self: 'New')
    case_id = fields.Many2one('patient.case', string='Patient', domain=[('state', '!=', 'done')], required=True)
    title = fields.Char(string='Title')
    nurse_id = fields.Many2one('hospital.staff', string='Nurse', domain="[('staff','=','nurse')]")
    doctor_id = fields.Many2one(related='case_id.doctor_id', string='Doctor')
    room_id = fields.Many2one('hospital.room', required=True)
    bed_id = fields.Many2one('hospital.bed', string='Table No',
                             domain="[('room_id','=',room_id),('stage', '=', 'free')]",
                             required=True)
    admit_date = fields.Datetime(string='Admit Date', default=fields.Datetime.now, required=True)
    discharge_date = fields.Datetime(string='Discharge Date', default=fields.Datetime.now, required=True)
    days = fields.Integer(compute='day_compute_hours', string='Days')
    hours = fields.Integer(compute='day_compute_hours', string='Hours')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    charges = fields.Monetary(compute='calculation_charges', string='Charges', store=True)
    stage = fields.Selection([('Draft', 'Draft'), ('Admit', 'Admit'),
                              ('Discharge', 'Discharge')], string='Stage', default='Draft')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('seq_no', 'New') == 'New':
                vals['seq_no'] = self.env['ir.sequence'].next_by_code('admit.patient') or 'New'
        res = super(HospitalAdmitPatient, self).create(vals_list)
        return res

    def action_admit(self):
        for rec in self:
            rec.stage = 'Admit'
        for res in self.bed_id:
            res.stage = 'book'
        return True

    def action_discharge(self):
        for rec in self:
            rec.stage = 'Discharge'
        for res in self.bed_id:
            res.stage = 'free'
        return True

    @api.depends('days')
    def calculation_charges(self):
        for rec in self.room_id:
            for res in self:
                res.charges = rec.charge * res.days

    @api.depends('discharge_date', 'admit_date')
    def day_compute_hours(self):
        for rec in self:
            discharge_date = fields.Datetime.to_datetime(rec.discharge_date)
            admit_date = fields.Datetime.to_datetime(rec.admit_date)
            daysLeft = discharge_date - admit_date

            years = ((daysLeft.total_seconds()) / (365.242 * 24 * 3600))
            yearsInt = int(years)
            months = (years - yearsInt) * 12
            monthsInt = int(months)
            days = (months - monthsInt) * (365.242 / 12)
            daysInt = int(days)
            rec.days = daysInt
            hours = (days - daysInt) * 24
            hoursInt = int(hours)
            minutes = (hours - hoursInt) * 60
            minutesInt = int(minutes)
            seconds = (minutes - minutesInt) * 60
            secondsInt = int(seconds)

            if days <= 0:
                rec.hours = 0
            else:
                days_hour = daysInt * 24
                rec.hours = hoursInt + days_hour
