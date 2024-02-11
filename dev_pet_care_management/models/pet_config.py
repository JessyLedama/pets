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


class pet_type(models.Model):
    _name = 'dev.pet.type'
    _description = 'Pet Type'
    
    name = fields.Char('Name', required="1")

    
class pet_category(models.Model):
    _name = 'dev.pet.category'
    _description = 'Pet Category'
    
    name = fields.Char('Name', required="1")


class pet_category(models.Model):
    _name = 'dev.pet.tags'
    _description = 'Pet Tags'
    
    name = fields.Char('Name', required="1")
    color = fields.Integer('Color', default=6)


class pet_medical_question(models.Model):
    _name = 'dev.medical.question'
    _description = 'Pet Medical Question'
    
    name = fields.Char('Name', required="1")

class pet_medical_ans(models.Model):
    _name = 'dev.medical.ans'
    _description = 'Pet Medical ans'
    
    name = fields.Char('Name', required="1")


class pet_vaccine(models.Model):
    _name = 'dev.pet.vaccine'
    _description = 'Pet Vaccine'
    
    name = fields.Char('Name', required="1")
    expire_on = fields.Integer('Expire On', default=2)


class boarding_type(models.Model):
    _name = 'dev.bording.type'
    _description = 'Bording Type'
    
    name = fields.Char('Name', required="1")
    charge = fields.Float('Charge')
    
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
