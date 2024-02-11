# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BillInherit(models.Model):
    _inherit = 'account.move'
    _description = __doc__

    maintenance_id = fields.Many2one(
        'hospital.maintenance', string='Maintenance')


class HospitalMaintenance(models.Model):
    """Hospital Maintenance"""
    _name = 'hospital.maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'seq_no'

    seq_no = fields.Char(string='Maintainable No', readonly=True,
                         copy=False, index=True, default=lambda self: 'New')
    type = fields.Selection([('room', 'Cleaning'), ('electrical', 'Electrical'), ('equipment', 'Equipment'),
                             ('other', 'Other')], string='Type')
    maintenance_date = fields.Date(string='Date')
    support_staff_ids = fields.Many2many(
        "hospital.staff", string="Support Staff", compute="_get_available_employee")
    cleaner_id = fields.Many2one('hospital.staff', string="Cleaner", domain="[('id','in', support_staff_ids),"
                                                                            "('department','=','Maintenance')]")
    description = fields.Char(string='Description')
    supplier_id = fields.Many2one(
        'res.partner', string='Supplier', required=True)
    stages = fields.Selection([('draft', "New"), ('in_progress', "In Progress"), ('complete', "Complete"),
                               ('cancel', "Cancel")], default='draft', string="Stages")
    maintenance_service_ids = fields.One2many(
        'maintenance.service', 'hospital_maintenance_id', string="Services")
    maintenance_charge = fields.Monetary(
        string="Total", compute="_total_maintenance_service_charge")
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', related="company_id.currency_id")
    supplier_bill_id = fields.Many2one('account.move', string="Supplier Bill")

    def draft_to_in_progress(self):
        for rec in self:
            rec.stages = 'in_progress'

    def in_progress_to_complete(self):
        for rec in self:
            rec.stages = 'complete'

    def complete_to_cancel(self):
        for rec in self:
            rec.stages = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('seq_no', 'New') == 'New':
                vals['seq_no'] = self.env['ir.sequence'].next_by_code(
                    'hospital.maintenance') or 'New'
        res = super(HospitalMaintenance, self).create(vals_list)
        return res

    def unlink(self):
        for rec in self:
            if rec.stages in ['in_progress', 'complete']:
                raise ValidationError(
                    _('You are not allowed to delete records in progress or complete stages.'))
            return super(HospitalMaintenance, self).unlink()

    @api.depends("maintenance_date")
    def _get_available_employee(self):
        employee_id = []
        for rec in self:
            if rec.maintenance_date:
                day = rec.maintenance_date.strftime("%A").lower()
                employee_id = self.env["hospital.staff"].sudo().search(
                    [('staff', '=', 'employee'), (day, '=', True)])
            rec.support_staff_ids = employee_id

    @api.depends('maintenance_service_ids')
    def _total_maintenance_service_charge(self):
        for rec in self:
            maintenance_charge = 0.0
            for charge in rec.maintenance_service_ids:
                maintenance_charge = maintenance_charge + charge.unit_price
            rec.maintenance_charge = maintenance_charge

    # @api.onchange('maintenance_date')
    # def _onchange_maintenance(self):
    #     for rec in self:
    #         if rec.maintenance_date:
    #             dt = rec.maintenance_date
    #             day = (dt.strftime('%A')).lower()
    #             employee = self.env['hospital.staff'].sudo().search(
    #                 [('staff', '=', 'employee'), (day, '=', True), ('department', '=', 'Maintenance')])
    #             return {'domain': {'cleaner_id': [('id', 'in', employee.ids)]}}

    def action_create_agent_bill(self):
        invoice_lines = []
        if not self.maintenance_service_ids:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': "Please first add maintenance services!",
                    'sticky': False,
                }
            }
            return message
        for recorde in self.maintenance_service_ids:
            maintenance_service = {
                'product_id': recorde.product_id.id,
                'quantity': recorde.qty,
                'price_unit': recorde.unit_price,
            }
            invoice_lines.append((0, 0, maintenance_service)),
        data = {
            'partner_id': self.supplier_id.id,
            'move_type': 'in_invoice',
            'invoice_date': fields.Datetime.now(),
            'invoice_line_ids': invoice_lines,
            'maintenance_id': self.id
        }
        supplier_bill_id = self.env['account.move'].sudo().create(data)
        supplier_bill_id.action_post()
        self.supplier_bill_id = supplier_bill_id.id
        self.stages = 'complete'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Supplier Bill',
            'res_model': 'account.move',
            'res_id': supplier_bill_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
