# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class MedicalReport(models.Model):
    """Medical Report"""
    _name = 'medical.report'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    bird_type = fields.Many2one('animal.type', string='Pet Type')
    price = fields.Monetary(string='Price')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
