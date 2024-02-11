# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PatientCase(models.Model):
    """Patient Case"""
    _name = 'patient.case'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'case_seq'

    case_seq = fields.Char(string='Case Number', readonly=True,
                           copy=False, index=True, default=lambda self: 'New')
    appointment_id = fields.Many2one('hospital.appointment',
                                     domain="[('state','=','in_consultation'),('service_type','=','Procedures')]",
                                     string='Appointment')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    appointment_date = fields.Datetime(string='Appointment Date')
    appointment_end_date = fields.Datetime(compute="get_appointment_end_date")
    doctor_ids = fields.Many2many(''
                                  'hospital.staff', string="Doctors", compute="_get_available_doctor")
    doctor_id = fields.Many2one('hospital.staff', string='Doctor',
                                domain="[('id', 'in', doctor_ids), ('staff', '=', 'doctor')]")
    state = fields.Selection([('draft', 'Draft'),
                              ('in_consultation', 'In Consultation'),
                              ('done', 'Close'),
                              ('cancel', 'Cancel')],
                             string='State', default='draft', required=True)
    invoice_state = fields.Boolean(string='Invoice State', default=False)
    disease_description = fields.Text(string='Disease Description')
    followup = fields.Html(string='Remark')
    is_any_treatment = fields.Boolean(string='Treatment')
    is_vaccination = fields.Boolean(string='Vaccination')
    is_admit = fields.Boolean()
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    case_invoice_id = fields.Many2one('account.move', string='Case Invoice ')

    # One 2 many
    treatment_ids = fields.One2many(
        'medical.treatment', 'case_id', string='Treatments')
    admit_ids = fields.One2many('admit.patient', 'case_id')
    disease_ids = fields.Many2many('hospital.disease.type', string='Diseases')
    report_ids = fields.One2many(
        'patient.report', 'case_id', string="Patient Report")
    case_invoice_ids = fields.One2many(
        'case.invoice', 'case_id', string="Case Invoice")
    prescription_ids = fields.One2many(
        'hospital.prescription', 'case_id', string='Prescription')
    patient_report_ids = fields.One2many(
        'patient.report', 'case_id', string='Report')
    vaccination_ids = fields.One2many(
        'hospital.vaccination.details', 'case_id', string='Vaccination Details')
    surgery_ids = fields.One2many(
        'hospital.surgery', 'case_id', string='Surgery')

    # Charges
    total_treatment_charge = fields.Monetary(
        string='Total Treatment Charges', compute='_compute_treatment_charge')
    total_vaccination_charge = fields.Monetary(string='Total Vaccination Charges',
                                               compute='_compute_vaccination_charge')
    total_report_charge = fields.Monetary(
        string='Total Report Charges', compute='_compute_report_charge')
    total_surgery_charge = fields.Monetary(
        string='Total Surgery Charges', compute='_compute_surgery_charge')
    total_invoiced = fields.Monetary(string='Invoice')
    charges = fields.Monetary(string='Charge', store=True)

    # Count
    prescription_count = fields.Integer(
        string='Prescription Count', compute='compute_count')
    patient_report_count = fields.Integer(
        string='Report Count', compute='compute_count')
    surgery_count = fields.Integer(string='Surgeries', compute='compute_count')
    medical_bill_count = fields.Integer(
        string="Medical Bill Count", compute='compute_count')
    invoice_count = fields.Integer(
        string="Medical Invoice Count", compute='compute_count')

    # Patient Admit Details
    room_id = fields.Many2one('hospital.room')
    bed_id = fields.Many2one('hospital.bed', string='Table No',
                             domain="[('room_id','=',room_id),('stage', '=', 'free')]")
    nurse_id = fields.Many2one(
        'hospital.staff', string='Nurse', domain="[('staff','=','nurse'), ('id', 'in', available_nurse_ids)]")
    admit_date = fields.Datetime(string='Admit Date')
    discharge_date = fields.Datetime(string='Discharge Date')
    hours = fields.Float(string="Total Hours", compute='compute_hours')
    admit = fields.Boolean(string="Admit ")
    total_admit_charge = fields.Monetary(
        string='Total Admit Charges', compute='_compute_admit_charge')
    is_discharge = fields.Boolean(string="Is Discharge")
    admit_added = fields.Boolean()

    available_nurse_ids = fields.Many2many("hospital.staff", compute="_get_available_nurses")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    # Create, write, Constrain
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('case_seq', 'New') == 'New':
                vals['case_seq'] = self.env['ir.sequence'].next_by_code(
                    'patient.case') or 'New'
        res = super(PatientCase, self).create(vals_list)
        return res
    
    def unlink(self):
        for rec in self:
            if rec.state in ['in_consultation', 'done']:
                raise ValidationError(
                    _('You are not allowed to delete an appointment in the consultation or close state.'))
            return super(PatientCase, self).unlink()

    # onchange
    @api.onchange("appointment_date", 'doctor_id')
    def _onchange_appointment_date(self):
        for rec in self:
            records = self.env["patient.case"].sudo().search(
                [("doctor_id", "=", rec.doctor_id.id), ("state", "in", ["in_consultation", "draft"])])
            for data in records:
                if data.appointment_date and data.appointment_end_date:
                    if (data.appointment_date.date() == rec.appointment_date.date() and data.appointment_date.time() <=
                            rec.appointment_date.time() <= data.appointment_end_date.time()):
                        raise ValidationError(
                            f"In This Time Another Appointment for Doctor -  {rec.doctor_id.name} is already Scheduled."
                        )

    # Compute
    @api.depends("appointment_date")
    def _get_available_nurses(self):
        nurse_id = []
        for rec in self:
            if rec.appointment_date:
                dt = rec.appointment_date
                day = (dt.strftime('%A')).lower()
                nurse_id = self.env['hospital.staff'].sudo().search([('staff', '=', 'nurse'), (day, '=', True)])
            rec.available_nurse_ids = nurse_id

    @api.depends("appointment_date", "doctor_id")
    def get_appointment_end_date(self):
        for rec in self:
            if rec.appointment_date:
                rec.appointment_end_date = rec.appointment_date + \
                    timedelta(minutes=rec.doctor_id.duration_minutes)

    @api.depends('appointment_date')
    def _get_available_doctor(self):
        doctor_id = []
        for rec in self:
            if rec.appointment_date:
                day = rec.appointment_date.strftime('%A').lower()
                doctor_id = self.env["hospital.staff"].sudo().search(
                    [('staff', '=', 'doctor'), (day, '=', True)])
            rec.doctor_ids = doctor_id

    @api.depends('surgery_ids')
    def _compute_surgery_charge(self):
        for rec in self:
            total = 0.0
            for data in rec.surgery_ids:
                total = total + data.surgery_charge
            rec.total_surgery_charge = total
        return True

    @api.depends('admit_date', 'discharge_date')
    def compute_hours(self):
        for rec in self:
            hours = 0.0
            if rec.admit_date and rec.discharge_date:
                counted_hours = (rec.discharge_date -
                                 rec.admit_date).total_seconds() / 3600
                hours = counted_hours if counted_hours > 0 else 0.0
            rec.hours = hours

    def compute_count(self):
        for rec in self:
            case_invoice = self.env['case.invoice'].search(
                [('case_id', '=', self.id), ('invoice_id', '!=', False)]).mapped(
                'invoice_id').mapped('id')
            report_invoices = self.env['patient.report'].search(
                [('case_id', '=', self.id), ('invoice_id', '!=', False)]).mapped('invoice_id').mapped('id')
            rec.medical_bill_count = self.env['case.invoice'].search_count(
                [('case_id', '=', rec.id), '|', ('invoice_id.payment_state', '!=', 'paid'), ('invoice_id', '=', False)])
            rec.prescription_count = self.env['hospital.prescription'].search_count(
                [('case_id', '=', rec.id)])
            rec.patient_report_count = self.env['patient.report'].search_count(
                [('case_id', '=', rec.id)])
            rec.surgery_count = self.env['hospital.surgery'].search_count(
                [('case_id', '=', rec.id)])
            rec.invoice_count = len(case_invoice + report_invoices)

    @api.depends('hours', 'room_id.charge')
    def _compute_admit_charge(self):
        for rec in self:
            total = 0.0
            if rec.room_id:
                total = rec.hours * rec.room_id.charge
            rec.total_admit_charge = total

    @api.depends('treatment_ids')
    def _compute_treatment_charge(self):
        for rec in self:
            total = 0.0
            for data in rec.treatment_ids:
                total = total + data.charges
            rec.total_treatment_charge = total
        return True

    @api.depends('vaccination_ids')
    def _compute_vaccination_charge(self):
        for rec in self:
            total = 0.0
            for data in rec.vaccination_ids:
                total = total + data.charges
            rec.total_vaccination_charge = total
        return True

    @api.depends('patient_report_ids')
    def _compute_report_charge(self):
        for rec in self:
            total = 0.0
            for data in rec.patient_report_ids:
                total = total + data.price
            rec.total_report_charge = total
        return True

    # Button
    def action_confirm_appointment(self):
        self.state = 'in_consultation'
        self.start_date = fields.Date.today()
        self.action_add_doctor_charge()

    def action_cancel_appointment(self):
        self.state = 'cancel'

    def action_complete_case(self):
        if self.medical_bill_count == 0:
            self.state = 'done'
            self.end_date = fields.Date.today()
            if self.vaccination_ids:
                for data in self.vaccination_ids:
                    data.write({
                        'patient_id': self.patient_id.id,
                    })
            if self.disease_ids:
                prescription_records = self.env['hospital.prescription'].sudo().search([('case_id', '=', self.id)])
                medicines = []
                for rec in prescription_records:
                    meds = self.env["prescription.line"].sudo().search([('prescription_id', '=', rec.id)]).mapped(
                        'product_id.name')
                    medicines += meds
                medicine_name_str = ', '.join(medicines)
                self.env["hospital.disease"].create({
                    'disease_ids': self.disease_ids,
                    'patient_id': self.patient_id.id,
                    'start': self.start_date,
                    'end': self.end_date,
                    'medicine': medicine_name_str,
                    'disease_type': f'From Case > {self.disease_description}',
                })
        else:
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Invoice Payment Pending'),
                    'type': 'warning',
                    'message': _('You cannot close an appointment until all the invoices are paid.'),
                    'sticky': False,
                }
            }
            return notification
        
    def action_add_doctor_charge(self):
        desc = f"Consultancy Charges \n > of {self.doctor_id.name}"
        self.env["case.invoice"].create({
            'product_id': self.env.ref('tk_veterinary_management.consultancy_product_1').id,
            'case_id': self.id,
            'date': fields.Date.today(),
            'name': 'Doctor Charges',
            'desc': desc,
            'amount': self.doctor_id.consultancy_charge,
            'from_case': True
        })

    def action_admit_patient(self):
        self.bed_id.stage = 'book'
        self.admit = True

    def action_discharge_patient(self):
        self.discharge_date = fields.Datetime.now()
        self.bed_id.stage = 'free'
        self.is_discharge = True

    def action_close(self):
        for rec in self:
            rec.state = 'done'
            rec.appointment_id.state = 'done'
            rec.patient_id.stages = 'done'
        return True

    def action_add_treatment_charge(self):
        amount = 0.0
        desc = "Treatment" + "\n"
        for rec in self.treatment_ids:
            if not rec.charges_added:
                amount = amount + rec.charges
                desc = desc + " > " + str(rec.description) + " - " + str(rec.charges) + " " + str(
                    rec.currency_id.symbol) + "\n"
                rec.charges_added = True
        if amount > 0:
            self.env['case.invoice'].create({
                'product_id': self.env.ref('tk_veterinary_management.treatment_product_1').id,
                'case_id': self.id,
                'date': fields.Date.today(),
                'name': 'Treatment',
                'desc': desc,
                'amount': amount,
                'from_case': True
            })

    def action_add_admit_charge(self):
        desc = "Admit Charges" + "\n" + " > Admit for " + \
            str(round(self.hours, 2)) + " Hours"
        self.env['case.invoice'].create({
            'product_id': self.env.ref('tk_veterinary_management.admit_product_1').id,
            'case_id': self.id,
            'date': fields.Date.today(),
            'name': 'Patient Admit',
            'desc': desc,
            'amount': self.total_admit_charge,
            'from_case': True
        })
        self.admit_added = True

    def action_add_vaccination_charge(self):
        amount = 0.0
        desc = "Vaccination Charges" + "\n"
        for rec in self.vaccination_ids:
            if not rec.charges_added:
                amount = amount + rec.charges
                desc = desc + " > " + str(rec.vaccination_name.name) + " - " + str(rec.charges) + " " + str(
                    rec.currency_id.symbol) + "\n"
                rec.charges_added = True
        if amount > 0:
            self.env['case.invoice'].create({
                'product_id': self.env.ref('tk_veterinary_management.vaccination_product_1').id,
                'case_id': self.id,
                'date': fields.Date.today(),
                'name': 'Vaccination',
                'desc': desc,
                'amount': amount,
                'from_case': True
            })

    # Smart button
    def action_prescription(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'hospital.prescription',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_medical_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pending Medical Bills',
            'res_model': 'case.invoice',
            'domain': [('case_id', '=', self.id), '|', ('invoice_id.payment_state', '!=', 'paid'), ('invoice_id', '=', False)],
            'context': {'default_case_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_patient_report_count(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reports',
            'res_model': 'patient.report',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id, 'create': False},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_surgeries(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Surgeries',
            'res_model': 'hospital.surgery',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id, 'default_animal_id': self.patient_id.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_medical_invoice(self):
        case_invoice = self.env['case.invoice'].search([('case_id', '=', self.id), ('invoice_id', '!=', False)]).mapped(
            'invoice_id').mapped('id')
        report_invoices = self.env['patient.report'].search(
            [('case_id', '=', self.id), ('invoice_id', '!=', False)]).mapped('invoice_id').mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('id', 'in', case_invoice + report_invoices)],
            'context': {'create': False},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_invoices_amount(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Case',
            'res_model': 'account.move',
            'res_id': self.case_invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_create_prescription(self):
        context = {
            'default_case_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Prescription'),
            'res_model': 'hospital.prescription',
            'context': context,
            'view_mode': 'form',
            'target': 'new'
        }

    def action_add_surgery(self):
        context = {
            'default_animal_id': self.patient_id.id,
            'default_case_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Surgeries'),
            'res_model': 'hospital.surgery',
            'context': context,
            'view_mode': 'form',
            'target': 'new'
        }
    
    # scheduler
    @api.model
    def validate_appointment_status(self):
        today = datetime.date.today()
        cases_records = self.env["patient.case"].sudo().search([('state', '=', 'draft')])
        for rec in cases_records:
            if rec.appointment_date.date() < datetime.date.today():
                rec.write = {'state': 'cancel'}
        grooming_records = self.env["grooming.details"].sudo().search([('state', '=', 'draft')])
        for rec in grooming_records:
            if rec.appointment_date.date() < today:
                rec.write = {'state': 'cancel'}
        training_records = self.env["training.details"].sudo().search([('state', '=', 'draft')])
        for rec in training_records:
            if rec.appointment_date.date() < today:
                rec.write = {'state': 'cancel'}


class MedicalTreatment(models.Model):
    """Medical Treatment"""
    _name = 'medical.treatment'
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(string='Title')
    description = fields.Char(string='Descriptions')
    precautions = fields.Char(string='Precautions')
    charges = fields.Monetary(string='Charges', store=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    case_id = fields.Many2one('patient.case')
    charges_added = fields.Boolean()


class CaseInvoice(models.Model):
    _name = 'case.invoice'
    _description = "Case Invoice"

    case_id = fields.Many2one('patient.case', string="Case")
    product_id = fields.Many2one('product.product', string="Service Type")
    name = fields.Char(string="Invoice For")
    date = fields.Date(string="Date")
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    amount = fields.Monetary(string="Amount")
    desc = fields.Text(string="Description")
    from_case = fields.Boolean()
    invoice_id = fields.Many2one('account.move', string="Invoice")
    payment_state = fields.Selection(
        related="invoice_id.payment_state", string="Payment State")

    def unlink(self):
        for rec in self:
            if rec.invoice_id.state == "posted":
                raise ValidationError(_("You are not allowed delete posted invoice."))
            return super(CaseInvoice, self).unlink()

    def action_create_invoice(self):
        invoice_id = self.env['account.move'].create({
            'partner_id': self.case_id.patient_id.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': self.date,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'name': self.desc if self.desc else self.name,
                'quantity': 1,
                'price_unit': self.amount,
            })]
        })
        self.invoice_id = invoice_id.id

    def create_multiple_invoice(self):
        active_ids = self._context.get('active_ids')
        invoice_record = self.browse(active_ids)
        partner = self.browse(active_ids).mapped('case_id').mapped(
            'patient_id').mapped('customer_id').mapped('id')
        if not len(partner) == 1:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'title': _('Please Select one Case Invoices Entry'),
                    'sticky': False,
                }
            }
            return message
        partner_id = partner[0]
        created_ids = [
            data.id for data in invoice_record if not data.invoice_id]
        invoice_id = self.env['account.move'].create({
            'partner_id': partner_id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': data.product_id.id,
                'name': data.desc if data.desc else data.name,
                'quantity': 1,
                'price_unit': data.amount,
            }) for data in invoice_record if not data.invoice_id]
        })
        invoice_ids = self.browse(created_ids)
        for data in invoice_ids:
            data.invoice_id = invoice_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Invoice',
            'res_model': 'account.move',
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
