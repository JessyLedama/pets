# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class MaintenanceService(models.Model):
    """Maintenance Service"""
    _name = 'maintenance.service'
    _description = __doc__
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', required=True, string='Product')
    description = fields.Char(string="Description")
    qty = fields.Integer(string="Quantity", default=1)
    unit_price = fields.Monetary(string="Unit Price")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    hospital_maintenance_id = fields.Many2one('hospital.maintenance')

    @api.onchange('product_id')
    def maintenance_product_amount(self):
        for rec in self:
            if rec.product_id:
                rec.unit_price = rec.product_id.lst_price
