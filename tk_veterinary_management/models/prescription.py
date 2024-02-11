# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PatientProduct(models.Model):
    _inherit = 'product.template'

    is_medicine = fields.Boolean(string='Medicine')
    is_grooming_product = fields.Boolean(string='Grooming Product')
    medicine_form = fields.Selection([('liquid', 'Liquid'),
                                      ('tablet', 'Tablet'),
                                      ('capsules', 'Capsules'),
                                      ('suppositories', 'Suppositories'),
                                      ('drops', 'Drops'),
                                      ('inhalers', 'Inhalers'),
                                      ('injections', 'Injections'),
                                      ('patches', 'Patches')],
                                     string='Form')
    pack_size = fields.Char(string='Pack Size')


class HospitalPrescription(models.Model):
    """Hospital Prescription"""
    _name = 'hospital.prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'prescription_no'

    prescription_no = fields.Char(string='Prescription No.', required=True, readonly=True,
                                  default=lambda self: _('New'))
    case_id = fields.Many2one('patient.case', string='Animal', domain=[
                              ('state', '!=', 'done')], required=True)
    customer_id = fields.Many2one(
        related='case_id.patient_id.customer_id', string="Customer")
    doctor_id = fields.Many2one(related='case_id.doctor_id', string='Doctor')
    prescription_date = fields.Date(string='Date', default=fields.Date.today())
    prescription_line_ids = fields.One2many(
        'prescription.line', 'prescription_id', string='Prescription Lines')
    stage = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')], string='Stage', default='draft')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    pharmacists_ids = fields.Many2many(
        "res.users", compute="_get_pharmacists_ids")
    pharmacist_id = fields.Many2one(
        'res.users', string="Pharmacist", required=True, domain="[('id','in',pharmacists_ids)]")
    company_id = fields.Many2one(
        'res.company', string='Company', index=True, default=lambda self: self.env.company)

    is_doctor = fields.Boolean(compute="_compute_is_doctor")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('prescription_no', _('New')) == _('New'):
                vals['prescription_no'] = self.env['ir.sequence'].next_by_code(
                    'hospital.prescription') or _('New')
        res = super(HospitalPrescription, self).create(vals_list)
        return res

    def unlink(self):
        for rec in self:
            if rec.sale_order_id:
                if rec.sale_order_id.state == 'sale':
                    raise ValidationError(
                        _("You are not allowed to delete a record with a created sale order."))
            return super(HospitalPrescription, self).unlink()

    def _compute_is_doctor(self):
        if self.env.user.has_group("tk_veterinary_management.veterinary_doctor"):
            self.is_doctor = True
        else:
            self.is_doctor = False

    @api.depends("pharmacist_id")
    def _get_pharmacists_ids(self):
        for rec in self:
            emp_ids = []
            records = self.env["res.users"].sudo().search([])
            for data in records:
                if data.has_group("tk_veterinary_management.veterinary_pharmacist"):
                    emp_ids.append(data.id)
            rec.pharmacists_ids = emp_ids

    def action_create_sale_order(self):
        sale_order_id = self.env['sale.order'].sudo().create({
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': [(0, 0, {
                'product_id': medicine.product_id.product_variant_id.id,
                'product_uom_qty': medicine.quantity,
                'price_unit': medicine.price,
                'name': medicine.product_id.name,
            }) for medicine in self.prescription_line_ids],
        })
        self.sale_order_id = sale_order_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'res_id': sale_order_id.id,
            'view_mode': 'form',
            'target': 'current'
        }


class IntakeMedicine(models.Model):
    """Intake Medicine"""
    _name = 'intake.medicine'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char('Intake Time', required=True)


class PrescriptionLine(models.Model):
    """Prescription Line"""
    _name = 'prescription.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.template', string='Medicine', required=True,
                                 domain="[('is_medicine', '=', True),('type','=','product')]")
    price = fields.Float(related='product_id.list_price', string='Price')
    tax_ids = fields.Many2many(related='product_id.taxes_id', string='Taxes')
    intake_ids = fields.Many2many(
        'intake.medicine', string='Intake Time', required=True)
    quantity = fields.Integer(string='Qty.', default=1)
    form = fields.Selection(related='product_id.medicine_form', string='Form')
    duration = fields.Integer(string='Duration(Days)', default=30)
    frequency = fields.Char(string='Frequency', default='Daily', required=True)
    prescription_id = fields.Many2one(
        'hospital.prescription', string='Prescription')
