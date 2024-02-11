# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import json 

class dev_pet_boarding(models.Model):
    _name = "dev.pet.boarding"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Pet Bording"
    _order = 'name desc'
    
    name = fields.Char('Name', default='New', copy=False, tracking=1)
    from_date = fields.Date('Drop Date', required="1", tracking=2, copy=False, default=fields.datetime.now())
    to_date = fields.Date('Pickup Date', required="1", tracking=2, copy=False, default=fields.datetime.now())
    color = fields.Integer('Color')
    bording_type_id = fields.Many2one('dev.bording.type', string='Bording Type', required="1")
    charge = fields.Monetary('Charge', required="1", tracking=3)
    days = fields.Integer('Days', compute='_get_days')
    total_charge = fields.Monetary('Total Charge', compute='_get_amount')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.company, required="1")
    user_id = fields.Many2one('res.users', string='User', default=lambda self:self.env.user)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self:self.env.company.currency_id)
    
    partner_id = fields.Many2one('res.partner', string='Name Of Contact', required="1", tracking=3)
    email = fields.Char('Email', tracking=3)
    mobile = fields.Char('Mobile', required="1")
    
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('in','IN'),('out','OUT'),
                              ('done','Done'),('cancel','Cancel')], string='State', 
                              default='draft', copy=False, tracking=1)
    
    pet_ids = fields.Many2many('dev.pet', string='Pets', copy=False)
    invoice_count = fields.Integer('Invoice Count', compute='_get_invoice_count')
    
    def _get_invoice_count(self):
        for rec in self:
            invoice_ids = self.env['account.move'].search([('boarding_id','=',rec.id)])
            rec.invoice_count = len(invoice_ids.ids)
            
    
    @api.depends('from_date','to_date')
    def _get_days(self):
        for rec in self:
            rec.days = 0
            if rec.to_date and rec.from_date:
                days = rec.to_date - rec.from_date
                rec.days = days.days + 1
     
    @api.depends('days','charge')
    def _get_amount(self):
        for rec in self:
            rec.total_charge = rec.days * rec.charge
    
    @api.onchange('bording_type_id')
    def onchange_boarding(self):
        if self.bording_type_id:
            self.charge = self.bording_type_id.charge
        else:
            self.charge = 0
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.mobile = self.partner_id.mobile or self.partner_id.phone or ''
            self.email = self.partner_id.email or ''
        else:
            self.mobile = ''
            self.email = ''
    
    @api.constrains('from_date','to_date')
    def check_date(self):
        today_date = date.today()
        for rec in self:
            if rec.from_date < today_date:
                raise ValidationError(_('Drop Date must be greater or same of today date.'))
            if rec.from_date and rec.to_date and rec.to_date < rec.from_date:
                raise ValidationError(_('Pickup Date must be greate then  or same of Drop Date')) 
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('dev.pet.boarding') or 'New'
        boarding_id = super(dev_pet_boarding, self).create(vals)
        if boarding_id.partner_id:
            if boarding_id.partner_id.id not in boarding_id.message_partner_ids.ids:
                boarding_id.message_subscribe(partner_ids=boarding_id.partner_id.ids)
        return boarding_id
    
    def unlink(self):
        for rec in self:
            if rec.state not in  ['draft','cancel']:
                raise ValidationError(_('Pet Boarding Delete on draft and cancel state.'))
        return super(dev_pet_boarding,self).unlink()   
    
    def get_product_lines(self):
        inv_line = []
        tax_ids = []
        product_id = self.company_id.boarding_product_id
        if product_id.taxes_id:
            tax_ids = product_id.taxes_id.ids
        price = self.total_charge
        inv_line.append((0,0,{
            'product_id':product_id.id,
            'quantity':1,
            'name':self.name + ' Boarding',
            'product_uom_id':product_id.uom_id and product_id.uom_id.id or False ,
            'price_unit':price,
            'tax_ids':[(6,0, tax_ids)],
            }))
        
        return inv_line
        
    def create_customer_invoice(self):
        journal_pool = self.env['account.journal'].sudo()
        journal_id = journal_pool.search([('type','=','sale')],limit=1)
        if not journal_id:
            raise ValidationError(_('Please Create Sale Journal'))
        if not self.company_id.boarding_product_id:
            raise ValidationError(_('Please Select Boarding Product in Pet Care Setting.'))
        vals = {
                'partner_id': self.partner_id and self.partner_id.id or False,
                'invoice_line_ids': self.get_product_lines(),
                'boarding_id':self.id,
                'move_type':'out_invoice',
                'journal_id': journal_id and journal_id.id or False,
                'currency_id': self.currency_id and self.currency_id.id,
                }
        invoice_id = self.env['account.move'].create(vals)
    
    def action_confirm(self):
        if not self.pet_ids:
            raise ValidationError(_('Please Select Pets For Boarding.'))
        self.state = 'confirm'
    
    def get_payment_ids(self,invoice):
        payment = invoice.invoice_payments_widget
        payment_ids = []
        if payment:
            payment_dic = json.loads(payment) 
            if payment_dic:
                payment_dic = payment_dic.get('content')
                for payment in payment_dic:
                    if payment.get('account_payment_id'):
                        payment_ids.append(payment.get('account_payment_id'))
                if payment_ids:
                    payment_ids = self.env['account.payment'].browse(payment_ids)
                    return payment_ids
        return payment_ids
        
        
    def action_cancel(self):
        self.state = 'cancel'
        invoice_ids = self.env['account.move'].sudo().search([('boarding_id','=',self.id)])
        for invoice in invoice_ids:
            pay_ids = self.get_payment_ids(invoice)
            if pay_ids:
                for payment in pay_ids:
                    if payment.state in ['posted','reconciled']:
                        payment.action_draft()
                        payment.action_cancel()
                        payment.unlink()
            invoice.button_draft()
            invoice.sudo().button_cancel()
            
        for pet in self.pet_ids:
            pet.is_boarding = False
            
    def action_in(self):
        invoice_id = self.env['account.move'].search([('boarding_id','=',self.id)])
        if not invoice_id:
            raise ValidationError(_('Please Create Invoice and Pay the invoice.'))
        if invoice_id:
            if invoice_id.payment_state != 'paid':
                raise ValidationError(_('Please Paid the Boarding Invoice.'))
        self.state = 'in'
        for pet in self.pet_ids:
            pet.is_boarding = True
    
    def action_out(self):
        self.state = 'out'
        for pet in self.pet_ids:
            pet.is_boarding = False
            
    def action_done(self):
        self.state = 'done'
    
    def action_draft(self):
        invoice_ids = self.env['account.move'].sudo().search([('boarding_id','=',self.id)])
        for invoice in invoice_ids:
            invoice.boarding_id = False
        self.state = 'draft'
    
    
    def action_view_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        invoice_ids = self.env['account.move'].search([('boarding_id','=',self.id),
                                                       ('move_type','=','out_invoice')])
        if invoice_ids:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoice_ids.id
            action['context']={
                'create':0,
                }
            return action
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
