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
from dateutil.relativedelta import relativedelta



class dev_pet_boarding(models.Model):
    _name = 'dev.pet.boarding'
    _inherit = ['dev.pet.boarding','rating.mixin']
    
    
    feedback_rate = fields.Selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4')], default='0', string='Rate', compute='_get_rating_value', readonly=True)
    feedback_date = fields.Date('Feedback Date', compute='_get_rating_value', readonly=True)
    review = fields.Text('Review', compute='_get_rating_value', readonly=True)
    rating_image = fields.Binary('Image', compute='_get_rating_value', readonly=True)
    rating_text = fields.Selection([
        ('satisfied', 'Satisfied'),
        ('not_satisfied', 'Not satisfied'),
        ('highly_dissatisfied', 'Highly dissatisfied'),
        ('no_rating', 'No Rating yet')], string='Rating', readonly=True)
    
    
    def _get_rating_value(self):
        for request in self:
            request.write({
                'feedback_rate':False,
                'feedback_date':False,
                'rating_image':False,
                'review':'',
                'rating_text':False
            })
            rating_id = self.env['rating.rating'].search([('res_id','=',self.id),
                                                          ('res_model','=','dev.pet.boarding')], order='id desc', limit=1)
            if rating_id:
                rating = int(rating_id.rating)
                if rating > 4:
                    rating = 4
                request.write({
                    'feedback_rate':str(rating),
                    'feedback_date':rating_id.write_date,
                    'rating_image':rating_id.rating_image,
                    'review':rating_id.feedback,
                    'rating_text':rating_id.rating_text
                })
    
    def rating_apply(self, rate, token=None, feedback=None, subtype_xmlid=None):
        return super(dev_pet_boarding, self).rating_apply(rate, token=token, feedback=feedback, subtype_xmlid="dev_pet_care_rating.mt_pet_boarding_rating")

    def _rating_get_parent_field_name(self):
        return 'partner_id'
    
    def rating_get_partner_id(self):
        res = super(dev_pet_boarding, self).rating_get_partner_id()
        if not res and self.partner_id:
            return self.partner_id
        return res
    
    def _send_courier_rating_mail(self, force_send=False):
        for request in self:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('dev_pet_care_rating.rating_pet_boarding_request_email_template', raise_if_not_found=False)
            if template_id:
                template_id = self.env['mail.template'].browse(template_id)
                request.rating_send_request(template_id, lang=request.partner_id.lang, force_send=force_send)
                
                
    def send_mail_for_rating(self):
        if self.partner_id:
            self._send_courier_rating_mail()
    
    
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
