# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

#    def view_membership(self):
#        ctx = dict(create=False)
#        return {
#            'type': 'ir.actions.act_window',
#            'name': 'Membership',
#            'res_model': 'dev.membership',
#            'domain': [('product_id.name', '=', self.name)],
#            'view_mode': 'tree,form',
#            'target': 'current',
#            'context': ctx,
#        }

#    def _get_membership_count(self):
#        for rec in self:
#            membership_count = self.env['dev.membership'].search_count([('product_id.name', '=', rec.name)])
#            rec.membership_count = membership_count

    is_pet_service = fields.Boolean(string="Pet Service")

class ProductProduct(models.Model):
    _inherit = "product.product"

    def view_membership(self):
        ctx = dict(create=False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Membership',
            'res_model': 'dev.membership',
            'domain': [('product_id.name', '=', self.name)],
            'view_mode': 'tree,form',
            'target': 'current',
            'context': ctx,
        }
