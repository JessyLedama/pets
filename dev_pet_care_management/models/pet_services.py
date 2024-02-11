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

class dev_pet_service(models.Model):
    _name = "dev.pet.service"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Pet Service"
    _order = 'name desc'
    
    name = fields.Char('Name', default='New', copy=False, tracking=1)
    date = fields.Date('Date', tracking=2, required=1, default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Client', required="1", tracking=1)
    email = fields.Char('Email')
    mobile = fields.Char('Mobile', required="1")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.company, required="1")
    user_id = fields.Many2one('res.users', string='User', default=lambda self:self.env.user)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self:self.env.company.currency_id)
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('done','Done'),('cancel','Cancel')], string='State', 
                              default='draft', copy=False, tracking=1)
    invoice_count = fields.Integer('Invoice Count', compute='_get_invoice_count')
    service_lines = fields.One2many('pet.service.lines','service_id', string='Service Lines')
    total_amount = fields.Monetary('Total Amount', compute='_get_amount')
    notes = fields.Text('Notes')
    
    @api.depends('service_lines', 'service_lines.price')
    def _get_amount(self):
        for rec in self:
            price = 0
            for line in rec.service_lines:
                price += line.price
            rec.total_amount = price
    
    def _get_invoice_count(self):
        for rec in self:
            invoice_ids = self.env['account.move'].search([('pet_service_id','=',rec.id)])
            rec.invoice_count = len(invoice_ids.ids)
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.mobile = self.partner_id.mobile or self.partner_id.phone or ''
            self.email = self.partner_id.email or ''
        else:
            self.mobile = ''
            self.email = ''
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('dev.pet.service') or 'New'
        service_id = super(dev_pet_service, self).create(vals)
        if service_id.partner_id:
            if service_id.partner_id.id not in service_id.message_partner_ids.ids:
                service_id.message_subscribe(partner_ids=service_id.partner_id.ids)
        return service_id
    
    def unlink(self):
        for rec in self:
            if rec.state not in  ['draft','cancel']:
                raise ValidationError(_('Pet Service Delete on draft and cancel state.'))
        return super(dev_pet_service,self).unlink()   
    
    def get_product_lines(self):
        inv_line = []
        tax_ids = []
        product_id = self.company_id.service_product_id
        if product_id.taxes_id:
            tax_ids = product_id.taxes_id.ids
        for line in self.service_lines:
            ser_name = ''
            for pro in line.service_ids:
                if ser_name:
                    ser_name = ser_name + ' ,'+ pro.name
                else:
                    ser_name = pro.name
            inv_line.append((0,0,{
                'product_id':product_id.id,
                'quantity':1,
                'name':ser_name + ' Pet Services',
                'product_uom_id':product_id.uom_id and product_id.uom_id.id or False ,
                'price_unit':line.price,
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
                'pet_service_id':self.id,
                'move_type':'out_invoice',
                'journal_id': journal_id and journal_id.id or False,
                'currency_id': self.currency_id and self.currency_id.id,
                }
        invoice_id = self.env['account.move'].create(vals)
    
    def action_confirm(self):
        if not self.service_lines:
            raise ValidationError(_('Please Select Service Lines.'))
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
        invoice_ids = self.env['account.move'].sudo().search([('pet_service_id','=',self.id)])
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
        self.state = 'cancel'
            
    def action_done(self):
        invoice_id = self.env['account.move'].search([('pet_service_id','=',self.id)])
        if not invoice_id:
            raise ValidationError(_('Please Create Invoice.'))
        if invoice_id and invoice_id.payment_state != 'paid':
            raise ValidationError(_('Please Paid Reaming invoice amount.'))
        self.state = 'done'
    
    def action_draft(self):
        invoice_ids = self.env['account.move'].sudo().search([('pet_service_id','=',self.id)])
        for invoice in invoice_ids:
            invoice.pet_service_id = False
        self.state = 'draft'
    
    
    def action_view_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        invoice_ids = self.env['account.move'].search([('pet_service_id','=',self.id),
                                                       ('move_type','=','out_invoice')])
        if invoice_ids:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoice_ids.id
            action['context']={
                'create':0,
                }
            return action
    
    def service_send_by_mail(self):
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('dev_pet_care_management.pet_service_email_template', raise_if_not_found=False)
        ctx = {
            'default_model': 'dev.pet.service',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

class pet_service_lines(models.Model):
    _name = 'pet.service.lines'
    _description = 'Pet Service Lines'
    
    
    pet_id = fields.Many2one('dev.pet', string='Pet', required="1")
    type_id = fields.Many2one('dev.pet.type', string='Type', related='pet_id.pet_type')
    service_ids = fields.Many2many('product.product', string='Services', required="1")
    price = fields.Monetary('Price')
    service_id = fields.Many2one('dev.pet.service', string='Service')
    currency_id = fields.Many2one('res.currency', related='service_id.currency_id')
    
    
    @api.onchange('service_ids')
    def onchange_service(self):
        price = 0
        for service in self.service_ids:
            price += service.list_price
        self.price = price
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
