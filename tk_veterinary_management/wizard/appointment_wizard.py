# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class NewAppointment(models.TransientModel):
    _name = 'appointment.wizard'
    _description = 'For creating New Appointment Using Wizard in patient'

    patient_id = fields.Many2one('hospital.patient', string='Patient')
    appointment_time = fields.Datetime(
        string='Time', default=fields.Datetime.now)
    doctor_id = fields.Many2one(
        'hospital.staff', string='Doctor', domain="[('staff','=','doctor')]")
    service_type = fields.Selection([('Procedures', 'Procedures'), ('Grooming', 'Grooming'), ('Training', 'Training')],
                                    string='Service Types', default='Procedures')
    message = fields.Text(compute="check_any_in_progress")
    is_message = fields.Boolean(default=False)

    @api.onchange('appointment_time')
    def _onchange_doctor_day(self):
        for rec in self:
            if rec.appointment_time:
                dt = rec.appointment_time
                day = (dt.strftime('%A')).lower()
                doctors = self.env['hospital.staff'].sudo().search(
                    [('staff', '=', 'doctor'), (day, '=', True)])
                return {'domain': {'doctor_id': [('id', 'in', doctors.ids)]}}

    @api.onchange("appointment_time", 'doctor_id')
    def _onchange_appointment_date(self):
        for rec in self:
            records = self.env["patient.case"].sudo().search(
                [("doctor_id", "=", rec.doctor_id.id), ("state", "in", ["in_consultation", "draft"])])
            for data in records:
                if data.appointment_date and data.appointment_end_date:
                    if (data.appointment_date.date() == rec.appointment_time.date() and data.appointment_date.time() <=
                            rec.appointment_time.time() <= data.appointment_end_date.time()):
                        raise ValidationError(
                            f"In This Time Another Appointment for Doctor - {rec.doctor_id.name} is already Scheduled."
                        )

    @api.depends('service_type')
    def check_any_in_progress(self):
        procedure_records = self.env["patient.case"].sudo().search([])
        grooming_records = self.env["grooming.details"].sudo().search([])
        training_records = self.env["training.details"].sudo().search([])
        for rec in self:
            rec.is_message = False
            if rec.service_type == 'Procedures' and procedure_records:
                for data in procedure_records:
                    if data.patient_id == rec.patient_id and data.state == "in_consultation":
                        rec.message = f'There is one procedure appointment is active Case no-{data.case_seq}, time-{data.appointment_date} and the doctor is {data.doctor_id.name}'
            elif rec.service_type == "Grooming" and grooming_records:
                for data in grooming_records:
                    if data.patient_id == rec.patient_id and data.state == "in_consultation":
                        rec.message = f'There is one grooming appointment is active Case no-{data.grooming_no}, time-{data.appointment_date} and the grooming employee is {data.grooming_employee_id.name}'
            elif rec.service_type == 'Training' and training_records:
                for data in training_records:
                    if data.patient_id == rec.patient_id and data.state == "in_consultation":
                        rec.message = f'There is one grooming appointment is active Case no-{data.training_no}, time-{data.appointment_date} and the training employee is {data.training_employee_id.name}'

            if rec.message:
                rec.is_message = True

    def set_appointment(self):
        if self.service_type == 'Procedures':
            data = {
                'patient_id': self.patient_id.id,
                'appointment_date': self.appointment_time,
                'doctor_id': self.doctor_id.id,
            }
            case_id = self.env['patient.case'].create(data)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Procedure Case',
                'res_model': 'patient.case',
                'res_id': case_id.id,
                'view_mode': 'form',
                'target': 'current'
            }
        if self.service_type == 'Grooming':
            grooming_id = self.env['grooming.details'].create({
                'appointment_date': self.appointment_time,
                'patient_id': self.patient_id.id
            })
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
                'appointment_date': self.appointment_time,
                'patient_id': self.patient_id.id,
                'bird_type': self.patient_id.bird_type.id
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Training',
                'res_model': 'training.details',
                'res_id': training_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

        # data = {
        #     'patient_id': self.patient_id.id,
        #     'appointment_time': self.appointment_time,
        #     'doctor_id': self.doctor_id.id,
        #     'service_type': self.service_type
        # }
        # appointment_id = self.env['hospital.appointment'].create(data)
        # self.patient_id.draft_to_confirm()
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Appointment',
        #     'res_model': 'hospital.appointment',
        #     'res_id': appointment_id.id,
        #     'view_mode': 'form',
        #     'target': 'current'
        # }

    def set_new_appointment(self):
        rec = self._context.get('active_id')
        active_id = self.env['patient.case'].browse(rec)
        data = {
            'patient_id': active_id.patient_id.id,
            'appointment_time': self.appointment_time,
            'doctor_id': self.doctor_id.id,
            'service_type': self.service_type
        }
        appointment_id = self.env['hospital.appointment'].create(data)
        active_id.patient_id.stages = 'Active'
        return True
