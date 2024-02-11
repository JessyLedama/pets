# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HospitalSurgery(models.Model):
    """Hospital Surgery"""
    _name = 'hospital.surgery'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'surgery_code'

    surgery_code = fields.Char(
        string='Code', required=True, readonly=True, default=lambda self: _('New'))
    surgery_id = fields.Many2one(
        'surgery.details', string='Surgery', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    surgery_charge = fields.Monetary(
        related='surgery_id.charge', string='Estimated Cost')
    description = fields.Char(string='Description')
    schedule_date = fields.Datetime(string='Schedule Date')
    start_date = fields.Datetime(string='Start Time')
    end_date = fields.Datetime(string='End Time')
    surgery_type = fields.Selection([('immediate', 'Immediate'),
                                     ('urgent', 'Urgent'),
                                     ('expedited', 'Expedited'),
                                     ('elective', 'Elective')],
                                    string='Urgency', required=True, default='elective')
    agreement = fields.Binary(string='Agreement')
    agreement_name = fields.Char(string='File Name')

    animal_id = fields.Many2one(
        "hospital.patient", string="Patient", required=True)
    case_id = fields.Many2one('patient.case', string='Appointment',
                              domain="[('patient_id', '=', animal_id), ('state', '=', 'in_consultation')]", required=True)
    age = fields.Integer(related='case_id.patient_id.age', string='Age')
    doctor_ids = fields.Many2many(
        "hospital.staff", string="Doctors", compute="_get_available_doctors")
    doctor_id = fields.Many2one(
        'hospital.staff', string='Surgeon', required=True, domain="[('id', 'in', doctor_ids)]")
    supportive_doctor_ids = fields.Many2many('hospital.staff', string='Supportive Doctors',
                                             domain="[('id', 'in', doctor_ids), ('id', '!=', doctor_id)]")
    available_nurse_ids = fields.Many2many(
        "hospital.staff", compute="_get_available_nurses")
    nurse_ids = fields.Many2many('hospital.staff', 'hospital_nurse_surgery_rel', 'nurse_id', 'surgery_id',
                                 string='Nurses', domain="[('id', 'in', available_nurse_ids)]")
    tag_ids = fields.Many2many('surgeries.tag', string="Tags")
    stage = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('done', 'Complete'),
                              ('cancel', 'Cancel')], readonly=1, default='draft')
    
    invoice_id = fields.Many2one("account.move", string="Invoice")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('surgery_code', _('New')) == _('New'):
                vals['surgery_code'] = self.env['ir.sequence'].next_by_code(
                    'hospital.surgery') or _('New')
        res = super(HospitalSurgery, self).create(vals_list)
        return res

    def unlink(self):
        for rec in self:
            if rec.stage in ['in_progress', 'done']:
                raise ValidationError(_('You are not allowed delete record in progress or complete stage.'))
            return super(HospitalSurgery, self).unlink()

    @api.constrains("start_date", "end_date")
    def _check_end_time(self):
        if self.end_date < self.start_date:
            raise ValidationError(
                _("Surgery end time cannot be less than surgery start time."))

    def action_in_progress(self):
        for rec in self:
            rec.stage = 'in_progress'
        return True

    @api.depends("schedule_date")
    def _get_available_nurses(self):
        nurse_id = []
        for rec in self:
            if rec.schedule_date:
                dt = rec.schedule_date
                day = (dt.strftime('%A')).lower()
                nurse_id = self.env['hospital.staff'].sudo().search(
                    [('staff', '=', 'nurse'), (day, '=', True)])
            rec.available_nurse_ids = nurse_id

    @api.depends("schedule_date")
    def _get_available_doctors(self):
        doctor_id = []
        for rec in self:
            if rec.schedule_date:
                dt = rec.schedule_date
                day = (dt.strftime('%A')).lower()
                doctor_id = self.env['hospital.staff'].sudo().search(
                    [('staff', '=', 'doctor'), (day, '=', True)])
            rec.doctor_ids = doctor_id

    def action_complete(self):
        desc = "Surgery " + "\n" + " > Surgeries : " + str(self.surgery_id.name) + " - " + str(
            self.surgery_charge) + " " + str(self.currency_id.symbol)
        invoice_id = self.env['account.move'].create({
            'partner_id': self.animal_id.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref('tk_veterinary_management.surgery_product_1').id,
                'name': desc,
                'quantity': 1,
                'price_unit': self.surgery_charge,
            })]
        })
        self.invoice_id = invoice_id.id
        self.env['case.invoice'].create({
            'product_id': self.env.ref('tk_veterinary_management.surgery_product_1').id,
            'case_id': self.case_id.id,
            'date': fields.Date.today(),
            'name': 'Surgery Charges',
            'desc': desc,
            'invoice_id': self.invoice_id.id,
            'amount': self.surgery_charge,
            'from_case': True
        })
        self.stage = 'done'
        # self.env['case.invoice'].create({
        #     'product_id': self.env.ref('tk_veterinary_management.surgery_product_1').id,
        #     'case_id': self.case_id.id,
        #     'date': fields.Date.today(),
        #     'name': 'Surgery Charges',
        #     'desc': desc,
        #     'amount': self.surgery_charge,
        #     'from_case': True
        # })
        # self.stage = 'done'

    def action_cancel(self):
        for rec in self:
            rec.stage = 'cancel'
        return True


class SurgeryDetails(models.Model):
    """Surgery Details"""
    _name = 'surgery.details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string='Surgery', required=True)
    charge = fields.Monetary(string='Charges', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    duration = fields.Char(string='Surgery Duration')


class SurgeriesTags(models.Model):
    """Surgeries Tags"""
    _name = 'surgeries.tag'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'tags'

    color = fields.Integer(string='Color')
    tags = fields.Char(string='Surgery Tag', required=True)
