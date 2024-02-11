# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PatientReport(models.Model):
    """Patient Report"""
    _name = 'patient.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'case_id'

    case_id = fields.Many2one('patient.case', string='Patient')
    date = fields.Date(string='Date', default=fields.Date.today())
    report_id = fields.Many2one(
        'medical.report', string='Report', required=True)
    lab_tech_ids = fields.Many2many("res.users", compute="_get_lab_tech_ids")
    lab_technician_id = fields.Many2one('res.users', string="Lab Technician", domain="[('id','in',lab_tech_ids)]")
    report_document_ids = fields.One2many(
        'report.document', 'patient_report_id')
    # Currency
    price = fields.Monetary(related='report_id.price', string='Price')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    report_count = fields.Integer(
        string='Report Count', compute='_compute_report_count')
    stages = fields.Selection([('draft', "New"), ('in_progress', "In Progress"), ('complete', "Complete"),
                               ('cancel', "Cancel")], default='draft', string="Stages")
    document = fields.Binary(string='Documents')
    file_name = fields.Char(string='File Name')
    invoice_id = fields.Many2one('account.move', string="Invoice")

    # animal detail fields
    name = fields.Char(related="case_id.patient_id.patient_name")
    pet_type = fields.Many2one(
        "animal.type", related="case_id.patient_id.bird_type")
    breed = fields.Char(related="case_id.patient_id.bird")
    gender = fields.Selection(related="case_id.patient_id.gender")
    age = fields.Integer(related="case_id.patient_id.age")
    age_type = fields.Selection(related="case_id.patient_id.age_type")
    behaviour = fields.Char(
        related="case_id.patient_id.behaviour", string="Behavior")
    weight = fields.Float(related="case_id.patient_id.weight")
    height = fields.Char(related="case_id.patient_id.height")
    blood_type = fields.Char(related="case_id.patient_id.blood_type")
    rh = fields.Char(related="case_id.patient_id.rh")

    def unlink(self):
        for rec in self:
            if rec.stages in ['in_progress', 'complete']:
                raise ValidationError(
                    _('You are not allowed to delete records in progress or complete stages.'))
            return super(PatientReport, self).unlink()
        
    @api.depends("lab_technician_id")
    def _get_lab_tech_ids(self):
        for rec in self:
            emp_ids = []
            records = self.env["res.users"].sudo().search([])
            for data in records:
                if data.has_group("tk_veterinary_management.veterinary_lab_technician"):
                    emp_ids.append(data.id)
            rec.lab_tech_ids = emp_ids

    def draft_to_in_progress(self):
        for rec in self:
            rec.stages = 'in_progress'

    def action_create_invoice(self):
        invoice_id = self.env['account.move'].create({
            'partner_id': self.case_id.patient_id.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': self.date,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref('tk_veterinary_management.report_product_1').id,
                'name': self.report_id.name,
                'quantity': 1,
                'price_unit': self.price,
            })]
        })
        self.invoice_id = invoice_id.id
        self.stages = 'complete'

    def complete_to_cancel(self):
        for rec in self:
            rec.stages = 'cancel'

    @api.depends('report_document_ids')
    def _compute_report_count(self):
        for rec in self:
            count = self.env['report.document'].search_count(
                [('patient_report_id', '=', rec.id)])
            rec.report_count = count
        return True

    def action_report_document(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reports',
            'res_model': 'report.document',
            'domain': [('patient_report_id', '=', self.id)],
            'context': {'default_patient_report_id': self.id},
            'view_mode': 'tree',
            'target': 'current'
        }


class ReportDocument(models.Model):
    """Report Document"""
    _name = 'report.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'patient_report_id'

    patient_report_id = fields.Many2one(
        'patient.report', string='Patient', readonly=True)
    document_date = fields.Date(
        string='Date', default=fields.Date.today(), readonly=True)
    report_id = fields.Many2one(
        related='patient_report_id.report_id', string='Report')
    document = fields.Binary(string='Documents', required=True)
    file_name = fields.Char(string='File Name')
