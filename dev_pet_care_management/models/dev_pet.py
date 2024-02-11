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


class dev_pet(models.Model):
    _name = "dev.pet"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Pet Animal / Bird"
    
    number = fields.Char('Number', default='New', copy=False)
    type = fields.Selection([('animal','Animal'),('bird','Bird')], default='animal', string='Type')
    image = fields.Image('Image')
    name = fields.Char('Name', required="1")
    owner_id = fields.Many2one('res.partner', string='Owner', required="1")
    veterinarian_id = fields.Many2one('hr.employee', string='Veterinarian', ondelete="restrict")
    pet_type = fields.Many2one('dev.pet.type', string='Type', required="1")
    category_id = fields.Many2one('dev.pet.category', string='Category', required="1")
    date_of_birth = fields.Date('Date of Birth')
    age = fields.Integer('Age', compute='_get_pet_age')
    color = fields.Char('Color')
    register_date = fields.Date('Register Date', required="1")
    user_id = fields.Many2one('res.users', string='Register By', default=lambda self:self.env.user)
    sex= fields.Selection([('male','Male'),('female','Female')], default='male', string='Sex')
    tags = fields.Many2many('dev.pet.tags', string='Tags')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.company)
    medical_lines = fields.One2many('dev.pet.medical.history', 'pet_id', string='Medical Lines')
    vaccine_lines = fields.One2many('dev.pet.vaccine.history', 'pet_id', string='Vaccine Lines')
    is_boarding = fields.Boolean('IS Boarding', default=False, copy=False)
    
    
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].sudo().next_by_code('dev.pet.sequence') or 'New'
        return super(dev_pet, self).create(vals)
    
    @api.depends('date_of_birth')
    def _get_pet_age(self):
        for pet in self:
            pet.age = 0
            if pet.date_of_birth:
                birthDate = pet.date_of_birth
                today = date.today()
                age = today.year - birthDate.year -((today.month, today.day) < (birthDate.month, birthDate.day))
                pet.age = age
            
        
        
    
class dev_pet_medical_history(models.Model):
    _name = 'dev.pet.medical.history'
    _description = 'Medical History'
    
    question_id = fields.Many2one('dev.medical.question', string='Question')
    ans_id = fields.Many2one('dev.medical.ans', string='Answer')
    pet_id = fields.Many2one('dev.pet', string='Pet', ondelete='cascade')


class dev_pet_vaccine_history(models.Model):
    _name = 'dev.pet.vaccine.history'
    _description = 'Vaccine History'
    
    vaccine_id = fields.Many2one('dev.pet.vaccine', string='Vaccine', required="1")
    date = fields.Date('Date Administered', required="1")
    expire_date = fields.Date('Expire Date')
    pet_id = fields.Many2one('dev.pet', string='Pet', ondelete='cascade')
    
    
    @api.onchange('date','vaccine_id')
    def onchange_vaccine(self):
        if self.vaccine_id and self.date:
            self.expire_date = self.date +relativedelta(years=self.vaccine_id.expire_on)
        else:
            self.expire_date = False
    
    


    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
