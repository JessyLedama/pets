# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class HospitalDisease(models.Model):
    _name = 'hospital.disease'
    _description = 'Animal Disease details and previously medical history'
    _rec_name = 'disease_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    patient_id = fields.Many2one('hospital.patient', string='Animal')
    patient_name = fields.Char(related='patient_id.patient_name')
    disease_id = fields.Many2one('hospital.disease.type', string='Diseases')
    disease_ids = fields.Many2many("hospital.disease.type", string='Diseases Names')
    disease_type = fields.Char(string='Disease Description')
    start = fields.Date(string='Start Date')
    end = fields.Date(string='End Date')
    allergy = fields.Selection([('y', 'Yes'),
                                ('n', 'No')],
                               string='Allergy', default='n')
    allergy_description = fields.Text(string='Allergy Description')
    medicine = fields.Char(string='Medicine Name')



