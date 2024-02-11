# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GroomingDetails(models.Model):
    _name = 'grooming.details'
    _description = 'Grooming Details'
    _rec_name = 'grooming_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    grooming_no = fields.Char(string='Sequence', readonly=True, copy=False, index=True,
                              default=lambda self: 'New')
    appointment_id = fields.Many2one('hospital.appointment',
                                     domain="[('state','=','in_consultation'),('service_type','=','Grooming')]",
                                     string='Appointment')
    patient_id = fields.Many2one('hospital.patient', string='Animal')
    appointment_date = fields.Datetime(string='Appointment Date')
    grooming_ids = fields.Many2many('grooming.type', string='Grooming Type')
    charge = fields.Monetary(compute='_compute_grooming_charge', string='Charge')
    grooming_emp_ids = fields.Many2many("res.users", compute="get_grooming_emp_ids")
    grooming_employee_id = fields.Many2one('res.users', string="Grooming Employee",
                                           domain="[('id', 'in', grooming_emp_ids)]")

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    state = fields.Selection(
        [('draft', 'Draft'), ('in_consultation', 'In Progress'), ('done', 'Close'), ('cancel', 'Cancel')],
        string='State', default='draft', required=True)
    grooming_product_ids = fields.One2many('grooming.product', 'grooming_id')
    total_charge = fields.Monetary(string='Total Price', compute='_compute_charge')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    is_invoice_created = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('grooming_no', 'New') == 'New':
                vals['grooming_no'] = self.env['ir.sequence'].next_by_code('grooming.details') or 'New'
        res = super(GroomingDetails, self).create(vals_list)
        return res

    def unlink(self):
        for rec in self:
            if rec.state in ['done', 'in_consultation']:
                raise ValidationError(
                    _('You are not allowed to delete an appointment in the consultation or close state.'))
            return super(GroomingDetails, self).unlink()

    def action_confirm_appointment(self):
        self.state = 'in_consultation'

    def action_cancel_appointment(self):
        self.state = 'cancel'

    @api.depends("grooming_employee_id")
    def get_grooming_emp_ids(self):
        for rec in self:
            emp_ids = []
            records = self.env["res.users"].sudo().search([])
            for data in records:
                if data.has_group("tk_veterinary_management.veterinary_grooming_employee"):
                    emp_ids.append(data.id)
            rec.grooming_emp_ids = emp_ids

    @api.depends('grooming_ids')
    def _compute_grooming_charge(self):
        for rec in self:
            total = 0.0
            if rec.grooming_ids:
                for data in rec.grooming_ids:
                    total = total + data.charge
            rec.charge = total
        return True

    @api.depends('grooming_product_ids')
    def _compute_charge(self):
        for rec in self:
            total = 0.0
            for data in rec.grooming_product_ids:
                total = total + data.price
            rec.total_charge = total
        return True

    def action_invoices(self):
        if self.grooming_product_ids:
            invoice_id = self.env['account.move'].sudo().create({
                'partner_id': self.patient_id.customer_id.id,
                'invoice_date': date.today(),
                'move_type': 'out_invoice',
                'invoice_line_ids': [(0, 0, {
                    'product_id': rec.product_id.product_variant_id.id,
                    'quantity': rec.quantity,
                    'name': rec.product_id.name,
                    'price_unit': rec.price,
                }) for rec in self.grooming_product_ids],
            })
            self.invoice_id = invoice_id.id
            # self.state = 'done'
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
            self.state = "done"
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


class GroomingType(models.Model):
    _name = 'grooming.type'
    _description = ' Grooming Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Grooming', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    charge = fields.Monetary(string='Price', store=True)


class GroomingProduct(models.Model):
    _name = 'grooming.product'
    _description = 'Grooming Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    grooming_id = fields.Many2one('grooming.details')
    product_id = fields.Many2one('product.template', string='Service', required=True,
                                 domain="[('is_grooming_product','=',True),('type','=','service')]")
    price = fields.Float(related='product_id.list_price', string='Price')
    quantity = fields.Integer(string='Qty.', default=1)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    total_product_charge = fields.Monetary(string='Net Total')
    desc = fields.Html(string="Description")

    @api.onchange('product_id')
    def onchange_desc(self):
        for rec in self:
            rec.desc = rec.product_id.description
