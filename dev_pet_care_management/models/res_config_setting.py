# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models,api,_
from odoo.exceptions import ValidationError



class res_company(models.Model):
    _inherit = 'res.company'
    
    boarding_product_id = fields.Many2one('product.product', string='Boarding Product')
    service_product_id = fields.Many2one('product.product', string='Service Product')
    
    
class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    boarding_product_id = fields.Many2one('product.product', 
                    related='company_id.boarding_product_id', 
                    readonly=False,
                    string='Boarding Product')
    
    service_product_id = fields.Many2one('product.product', 
                    related='company_id.service_product_id', 
                    readonly=False,
                    string='Service Product')
                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
