# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class AnimalType(models.Model):
    """Animal Type"""
    _name = 'animal.type'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char('Pet Type', required=True)


class HospitalDiseaseType(models.Model):
    """Hospital Disease Type"""
    _name = 'hospital.disease.type'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string='Name')


class ServiceType(models.Model):
    """Service Type"""
    _name = 'service.type'
    _description = 'Service Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Service Name', required=True)
