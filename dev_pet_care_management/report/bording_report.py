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


class pet_service_report(models.AbstractModel):
    _name = 'report.dev_pet_care_management.dev_pet_boarding_report'
    _description='Boarding Report'
    
    def get_selection_label(self, field_name, field_value):
        return _(dict(self.env['dev.pet.boarding'].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def _get_report_values(self, docids, data=None):
        docs = self.env['dev.pet.boarding'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'dev.pet.boarding',
            'docs': docs,
        }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
