# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class HospitalAppointment(models.Model):
    """Hospital Appointment"""
    _name = 'hospital.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('hospital.patient', string='Appointment', required=True)
    patient_name = fields.Char(related='patient_id.patient_name', string="Animal")
    service_type = fields.Selection([('Procedures', 'Procedures'), ('Grooming', 'Grooming'), ('Training', 'Training')],
                                    string='Service Type', required=True)
    case_id = fields.Many2one('patient.case', string='Case Number')
    doctor_id = fields.Many2one('hospital.staff', string='Doctor', domain="[('staff','=','doctor')]")
    appointment_time = fields.Datetime(string='Appointment Date', default=fields.Datetime.now, required=True)
    cancellation_reason = fields.Text(string="Cancellation Reasons")
    state = fields.Selection([('draft', 'Draft'),
                              ('in_consultation', 'In Progress'),
                              ('done', 'Close'),
                              ('cancel', "Cancel")],
                             string='Status', default='draft', required=True)

    def in_consultation_to_done(self):
        self.state = 'done'

    def done_to_cancel(self):
        self.state = 'cancel'

    def confirm_appointment(self):
        if self.service_type == 'Procedures':
            self.state = 'in_consultation'
        if self.service_type == 'Grooming':
            grooming_id = self.env['grooming.details'].create({
                'appointment_id': self.id,
                'grooming_employee_id': self.env.user.id
            })
            self.state = 'done'
            return {
                'type': 'ir.actions.act_window',
                'name': 'Grooming',
                'res_model': 'grooming.details',
                'res_id': grooming_id.id,
                'view_mode': 'form',
                'target': 'current'
            }
        if self.service_type == 'Training':
            training_id = self.env['training.details'].create({
                'appointment_id': self.id,
                'grooming_employee_id': self.env.user.id
            })
            self.state = 'done'
            return {
                'type': 'ir.actions.act_window',
                'name': 'Training',
                'res_model': 'training.details',
                'res_id': training_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

    # @api.onchange('appointment_time')
    # def _onchange_appointment(self):
    #     for rec in self:
    #         if rec.appointment_time:
    #             dt = rec.appointment_time
    #             day = (dt.strftime('%A')).lower()
    #             doctors = self.env['hospital.staff'].sudo().search([('staff', '=', 'doctor'), (day, '=', True)])
    #             return {'domain': {'doctor_id': [('id', 'in', doctors.ids)]}}

    def action_create_case(self):
        data = {
            'appointment_id': self.id
        }
        case_id = self.env['patient.case'].create(data)
        self.case_id = case_id.id
        self.state = 'done'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Case',
            'res_model': 'patient.case',
            'res_id': case_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
