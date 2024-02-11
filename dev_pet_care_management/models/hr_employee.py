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


class hr_employee(models.Model):
    _inherit = "hr.employee"
    
    is_veterinarian = fields.Boolean('Veterinarian')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
