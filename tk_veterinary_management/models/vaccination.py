# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class Vaccination(models.Model):
    """Vaccination"""
    _name = 'hospital.vaccination.details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'vaccination_name'

    patient_id = fields.Many2one('hospital.patient', string='Animal')
    case_id = fields.Many2one('patient.case', string='Case No.')
    patient_name = fields.Char(related='patient_id.patient_name')
    vaccination_name = fields.Many2one('animal.vaccine', string='Vaccine')
    vaccine_data = fields.Date(string='Vaccination Date')
    vaccine_end = fields.Date(string='End Date')
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    charges = fields.Monetary(string='Charges', store=True)
    charges_added = fields.Boolean()

    @api.onchange('vaccination_name')
    def onchange_get_charges_of_vaccine(self):
        for rec in self:
            if rec.vaccination_name:
                rec.charges = rec.vaccination_name.charges


class AnimalVaccine(models.Model):
    """Animal Vaccine"""
    _name = 'animal.vaccine'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string='Vaccine', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    charges = fields.Monetary(string='Charges', store=True)
