# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import pytz
import xlwt
import base64
from io import BytesIO
from odoo import fields, models


class AppointmentDetails(models.TransientModel):
    _name = 'appointment.details.wizard'
    _description = 'Find Patient list between to date '

    appointment_type = fields.Selection([("procedures", "Procedures"),
                                         ("grooming", "Grooming"),
                                         ("training", "Training")], string="Appointment Type", required=True, default="procedures")
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    # def action_details(self):
    #     patient_appointment_ids = self.env['hospital.appointment'].search(
    #         [('appointment_time', '>=', self.start_date),
    #          ('appointment_time', '<=', self.end_date)]).mapped('id')
    #     patient_browse_ids = self.env['hospital.appointment'].browse(patient_appointment_ids).mapped('id')

    #     workbook = xlwt.Workbook(encoding='utf-8')
    #     sheet1 = workbook.add_sheet('Appointment', cell_overwrite_ok=True)
    #     date_format = xlwt.XFStyle()
    #     date_format.num_format_str = 'mm/dd/yyyy'
    #     sheet1.col(0).width = 7000
    #     sheet1.write(0, 0, 'Animal')
    #     sheet1.write(0, 1, 'Date')
    #     sheet1.write(0, 2, ' Appointment Type')
    #     c = 1
    #     for data in patient_browse_ids:
    #         active_id = self.env['hospital.appointment'].browse(data)
    #         sheet1.col(c).width = 7000
    #         sheet1.write(c, 0, active_id.patient_id.patient_name)
    #         sheet1.write(c, 1, active_id.appointment_time, date_format)
    #         sheet1.write(c, 2, active_id.service_type)
    #         c += 1

    #     stream = BytesIO()
    #     workbook.save(stream)
    #     out = base64.encodebytes(stream.getvalue())

    #     attachment = self.env['ir.attachment'].sudo()
    #     filename = 'Appointment' + ".xlsx"
    #     attachment_id = attachment.create(
    #         {'name': filename,
    #          'type': 'binary',
    #          'public': False,
    #          'datas': out})
    #     if attachment_id:
    #         report = {
    #             'type': 'ir.actions.act_url',
    #             'url': '/web/content/%s?download=true' % (attachment_id.id),
    #             'target': 'self',
    #             'nodestroy': False,
    #         }
    #         return report
    def action_details(self):
        domain = [("appointment_date", ">=", self.start_date),
                  ("appointment_date", "<=", self.end_date)]
        if self.appointment_type == "procedures":
            procedure_records = self.env["patient.case"].sudo().search(domain)
            report = self.get_procedure_report(records=procedure_records)
            return report
        elif self.appointment_type == "grooming":
            grooming_records = self.env["grooming.details"].sudo().search(
                domain)
            report = self.get_grooming_report(records=grooming_records)
            return report
        elif self.appointment_type == "training":
            training_records = self.env["training.details"].sudo().search(
                domain)
            report = self.get_training_report(records=training_records)
            return report

    def get_training_report(self, records):
        workbook = xlwt.Workbook("utf-8")
        sheet = workbook.add_sheet("Training Appointments")
        sheet.show_grid = False
        title = xlwt.easyxf(
            "border: bottom thick,"
            "bottom_color sea_green; "
            "align: vert center, horz center;"
            "font: height 400, bold on, color-index dark_teal, name Century Gothic;"
        )
        sub_title = xlwt.easyxf(
            "border: bottom thick, left thin, right thin,"
            "bottom_color sea_green, right_color gray25, left_color gray25;"
            "align: vert center, horz center;"
            "font: height 200, bold on, color-index dark_teal, name Century Gothic;"
        )
        sub_title_right = xlwt.easyxf(
            "border: bottom thick, left thin, right thin,"
            "bottom_color sea_green, right_color gray25, left_color gray25;"
            "align: vert center, horz right;"
            "font: height 200, bold on, color-index dark_teal, name Century Gothic;"
        )
        border_all = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic;"
        )
        border_all_right = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz right;"
            "font: name Century Gothic;"
        )
        red_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_red, bold on;"
        )
        yellow_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_yellow, bold on;"
        )
        green_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_green, bold on;"
        )
        blue_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_blue, bold on;"
        )
        border_double_top = xlwt.easyxf(
            "border: top double, top_color gray80"
        )
        user_timezone = pytz.timezone(self.env.user.partner_id.tz)
        border_square = xlwt.Borders()
        border_square.top = xlwt.Borders.HAIR
        border_square.left = xlwt.Borders.HAIR
        border_square.right = xlwt.Borders.HAIR
        border_square.bottom = xlwt.Borders.HAIR
        border_square.top_colour = xlwt.Style.colour_map["gray25"]
        border_square.bottom_colour = xlwt.Style.colour_map["gray25"]
        border_square.right_colour = xlwt.Style.colour_map["gray25"]
        border_square.left_colour = xlwt.Style.colour_map["gray25"]
        al = xlwt.Alignment()
        al.horz = xlwt.Alignment.HORZ_CENTER
        al.vert = xlwt.Alignment.VERT_CENTER

        date_format = xlwt.XFStyle()
        date_format.num_format_str = "mm/dd/yyyy h:mm:ss"
        date_format.borders = border_square
        date_format.font.name = "Century Gothic"
        date_format.alignment = al

        date_format2 = xlwt.XFStyle()
        date_format2.num_format_str = "mm/dd/yyyy"
        date_format2.borders = border_square
        date_format2.font.name = "Century Gothic"
        date_format2.alignment = al

        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(2)
        sheet.row(0).height = 1000
        sheet.row(1).height = 500

        sheet.col(0).width = 400

        for i in range(1, 14):
            sheet.col(i).width = 5000
        sheet.col(5).width = 6000
        sheet.col(6).width = 6000
        sheet.col(8).width = 6000

        sheet.write_merge(0, 0, 1, 13, "TRAINING APPOINTMENT DETAILS", title)
        sheet.write(1, 1, "SEQUENCE", sub_title)
        sheet.write(1, 2, "ANIMAL", sub_title)
        sheet.write(1, 3, "ANIMAL TYPE", sub_title)
        sheet.write(1, 4, "BREED", sub_title)
        sheet.write(1, 5, "TRAINING EMPLOYEE", sub_title)
        sheet.write(1, 6, "APPOINTMENT DATE", sub_title)
        sheet.write(1, 7, "PACKAGE", sub_title)
        sheet.write(1, 8, "PACKAGE DURATION", sub_title)
        sheet.write(1, 9, "START DATE", sub_title)
        sheet.write(1, 10, "END DATE", sub_title)
        sheet.write(1, 11, "CERTIFICATE NO.", sub_title)
        sheet.write(1, 12, "CHARGES", sub_title_right)
        sheet.write(1, 13, "STATUS", sub_title)

        row = 2
        name = ""
        style = ""
        for rec in records:
            sheet.row(row).height = 400
            if rec.state == "complete":
                name = "Completed"
                style = green_font
            if rec.state == "in_consultation":
                name = "In Progress"
                style = yellow_font
            if rec.state == "cancel":
                name = "Cancelled"
                style = red_font
            if rec.state == "draft":
                name = "Draft"
                style = blue_font
            appointment_datetime = rec.appointment_date.astimezone(
                user_timezone)
            naive_datetime = appointment_datetime.replace(tzinfo=None)
            sheet.write(row, 1, rec.training_no, border_all)
            sheet.write(row, 2, rec.patient_id.patient_name, border_all)
            sheet.write(row, 3, rec.bird_type.name, border_all)
            sheet.write(row, 4, rec.bird, border_all)
            sheet.write(row, 5, rec.training_employee_id.name, border_all)
            sheet.write(row, 6, naive_datetime, date_format)
            if rec.package_id:
                sheet.write(row, 7, rec.package_id.name, border_all)
            else:
                sheet.write(row, 7, "", border_all)
            if rec.package_days > 0:
                sheet.write(row, 8, f"{rec.package_days} Days", border_all)
            else:
                sheet.write(row, 8, "", border_all)
            if rec.start_date:
                sheet.write(row, 9, rec.start_date, date_format2)
            else:
                sheet.write(row, 9, "", border_all)
            if rec.end_date:
                sheet.write(row, 10, rec.end_date, date_format2)
            else:
                sheet.write(row, 10, "", border_all)
            if rec.certificate_no:
                sheet.write(row, 11, rec.certificate_no, border_all)
            else:
                sheet.write(row, 11, "", border_all)
            sheet.write(
                row, 12, f"{rec.currency_id.symbol} {rec.charges}", border_all_right)
            sheet.write(row, 13, name, style)
            row += 1
        sheet.write_merge(row, row, 1, 13, "", border_double_top)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo()
        filename = 'Training Appointments' + ".xls"
        attachment_id = attachment.create(
            {'name': filename,
             'type': 'binary',
             'public': False,
             'datas': out})
        if attachment_id:
            report = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment_id.id,
                'target': 'self',
            }
            return report

    def get_grooming_report(self, records):
        workbook = xlwt.Workbook("utf-8")
        sheet = workbook.add_sheet("Grooming Appointments")
        sheet.show_grid = False

        title = xlwt.easyxf(
            "border: bottom thick,"
            "bottom_color sea_green; "
            "align: vert center, horz center;"
            "font: height 400, bold on, color-index dark_teal, name Century Gothic;"
        )
        sub_title = xlwt.easyxf(
            "border: bottom thick, left thin, right thin,"
            "bottom_color sea_green, right_color gray25, left_color gray25;"
            "align: vert center, horz center;"
            "font: height 200, bold on, color-index dark_teal, name Century Gothic;"
        )
        sub_title_right = xlwt.easyxf(
            "border: bottom thick, left thin, right thin,"
            "bottom_color sea_green, right_color gray25, left_color gray25;"
            "align: vert center, horz right;"
            "font: height 200, bold on, color-index dark_teal, name Century Gothic;"
        )
        border_all = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic;"
        )
        border_all_right = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz right;"
            "font: name Century Gothic;"
        )
        red_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_red, bold on;"
        )
        yellow_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_yellow, bold on;"
        )
        green_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_green, bold on;"
        )
        blue_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_blue, bold on;"
        )
        border_double_top = xlwt.easyxf(
            "border: top double, top_color gray80"
        )
        user_timezone = pytz.timezone(self.env.user.partner_id.tz)
        border_square = xlwt.Borders()
        border_square.top = xlwt.Borders.HAIR
        border_square.left = xlwt.Borders.HAIR
        border_square.right = xlwt.Borders.HAIR
        border_square.bottom = xlwt.Borders.HAIR
        border_square.top_colour = xlwt.Style.colour_map["gray25"]
        border_square.bottom_colour = xlwt.Style.colour_map["gray25"]
        border_square.right_colour = xlwt.Style.colour_map["gray25"]
        border_square.left_colour = xlwt.Style.colour_map["gray25"]
        date_format = xlwt.XFStyle()
        date_format.num_format_str = "mm/dd/yyyy h:mm:ss"
        date_format.borders = border_square
        date_format.font.name = "Century Gothic"
        al = xlwt.Alignment()
        al.horz = xlwt.Alignment.HORZ_CENTER
        al.vert = xlwt.Alignment.VERT_CENTER
        date_format.alignment = al

        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(2)
        sheet.row(0).height = 1000
        sheet.row(1).height = 500

        sheet.col(0).width = 400
        sheet.col(1).width = 4500
        sheet.col(2).width = 4000
        sheet.col(3).width = 6500
        sheet.col(4).width = 6500
        sheet.col(5).width = 4000
        sheet.col(6).width = 4500

        sheet.write_merge(0, 0, 1, 6, "GROOMING APPOINTMENT DETAILS", title)
        sheet.write(1, 1, "SEQUENCE", sub_title)
        sheet.write(1, 2, "ANIMAL", sub_title)
        sheet.write(1, 3, "GROOMING EMPLOYEE", sub_title)
        sheet.write(1, 4, "APPOINTMENT DATE", sub_title)
        sheet.write(1, 5, "TOTAL PRICE", sub_title_right)
        sheet.write(1, 6, "STATUS", sub_title)
        row = 2
        name = ""
        style = ""
        for rec in records:
            sheet.row(row).height = 400
            if rec.state == "done":
                name = "Closed"
                style = green_font
            if rec.state == "in_consultation":
                name = "In Progress"
                style = yellow_font
            if rec.state == "cancel":
                name = "Cancelled"
                style = red_font
            if rec.state == "draft":
                name = "Draft"
                style = blue_font
            appointment_datetime = rec.appointment_date.astimezone(
                user_timezone)
            naive_datetime = appointment_datetime.replace(tzinfo=None)
            sheet.write(row, 1, rec.grooming_no, border_all)
            sheet.write(row, 2, rec.patient_id.patient_name, border_all)
            sheet.write(row, 3, rec.grooming_employee_id.name, border_all)
            sheet.write(row, 4, naive_datetime, date_format)
            sheet.write(
                row, 5, f"{rec.currency_id.symbol} {rec.total_charge}", border_all_right)
            sheet.write(row, 6, name, style)
            row += 1
        sheet.write_merge(row, row, 1, 6, "", border_double_top)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo()
        filename = 'Grooming Appointments' + ".xls"
        attachment_id = attachment.create(
            {'name': filename,
             'type': 'binary',
             'public': False,
             'datas': out})
        if attachment_id:
            report = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment_id.id,
                'target': 'self',
            }
            return report

    def get_procedure_report(self, records):
        workbook = xlwt.Workbook("utf-8")
        sheet = workbook.add_sheet(
            "Procedure Appointments", cell_overwrite_ok=True)
        sheet.show_grid = False
        title = xlwt.easyxf(
            "border: bottom thick,"
            "bottom_color sea_green; "
            "align: vert center, horz center;"
            "font: height 400, bold on, color-index dark_teal, name Century Gothic;")
        sub_title = xlwt.easyxf(
            "border: bottom thick, left thin, right thin,"
            "bottom_color sea_green, right_color gray25, left_color gray25;"
            "align: vert center, horz center;"
            "font: height 200, bold on, color-index dark_teal, name Century Gothic;"
        )
        border_all = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic;"
        )
        border_all_big = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: height 220, name Century Gothic;"
        )
        red_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_red, bold on;"
        )
        yellow_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_yellow, bold on;"
        )
        green_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_green, bold on;"
        )
        blue_font = xlwt.easyxf(
            "border: bottom hair, left hair, right hair, top hair,"
            "bottom_color gray25, top_color gray25, left_color gray25, right_color gray25;"
            "align: vert center, horz center;"
            "font: name Century Gothic, color-index dark_blue, bold on;"
        )
        border_double_top = xlwt.easyxf(
            "border: top double, top_color gray80"
        )
        user_timezone = pytz.timezone(self.env.user.partner_id.tz)
        border_square = xlwt.Borders()
        border_square.top = xlwt.Borders.HAIR
        border_square.left = xlwt.Borders.HAIR
        border_square.right = xlwt.Borders.HAIR
        border_square.bottom = xlwt.Borders.HAIR
        border_square.top_colour = xlwt.Style.colour_map["gray25"]
        border_square.bottom_colour = xlwt.Style.colour_map["gray25"]
        border_square.right_colour = xlwt.Style.colour_map["gray25"]
        border_square.left_colour = xlwt.Style.colour_map["gray25"]
        date_format = xlwt.XFStyle()
        date_format.num_format_str = "mm/dd/yyyy h:mm:ss"
        date_format.borders = border_square
        date_format.font.name = "Century Gothic"
        al = xlwt.Alignment()
        al.horz = xlwt.Alignment.HORZ_CENTER
        al.vert = xlwt.Alignment.VERT_CENTER
        date_format.alignment = al

        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(2)
        sheet.row(0).height = 1000
        sheet.row(1).height = 500
        sheet.col(0).width = 400

        for i in range(1, 9):
            sheet.col(i).width = 4000
        sheet.col(4).width = 6500
        sheet.col(1).width = 4500
        sheet.col(8).width = 4500

        sheet.write_merge(0, 0, 1, 8, "PROCEDURE APPOINTMENT DETAILS", title)
        sheet.write(1, 1, "CASE NUMBER", sub_title)
        sheet.write(1, 2, "PATIENT", sub_title)
        sheet.write(1, 3, "DOCTOR", sub_title)
        sheet.write(1, 4, "APPOINTMENT DATE", sub_title)
        sheet.write(1, 5, "TREATMENT", sub_title)
        sheet.write(1, 6, "IS ADMIT", sub_title)
        sheet.write(1, 7, "VACCINATION", sub_title)
        sheet.write(1, 8, "STATUS", sub_title)

        row = 2
        name = ""
        style = ""
        for rec in records:
            appointment_datetime = rec.appointment_date.astimezone(
                user_timezone)
            naive_datetime = appointment_datetime.replace(tzinfo=None)
            if rec.is_any_treatment:
                treatment = "✔️"
            else:
                treatment = ""
            if rec.is_admit:
                admit = "✔️"
            else:
                admit = ""
            if rec.is_vaccination:
                vaccination = "✔️"
            else:
                vaccination = ""
            if rec.state == "done":
                name = "Closed"
                style = green_font
            if rec.state == "in_consultation":
                name = "In Consultation"
                style = yellow_font
            if rec.state == "cancel":
                name = "Cancelled"
                style = red_font
            if rec.state == "draft":
                name = "Draft"
                style = blue_font
            sheet.row(row).height = 400
            sheet.write(row, 1, rec.case_seq, border_all)
            sheet.write(row, 2, rec.patient_id.patient_name, border_all)
            sheet.write(row, 3, rec.doctor_id.name, border_all)
            sheet.write(row, 4, naive_datetime, date_format)
            sheet.write(row, 5, treatment, border_all_big)
            sheet.write(row, 6, admit, border_all_big)
            sheet.write(row, 7, vaccination, border_all_big)
            sheet.write(row, 8, name, style)
            row += 1

        sheet.write_merge(row, row, 1, 8, "", border_double_top)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo()
        filename = 'Procedure Appointments' + ".xls"
        attachment_id = attachment.create(
            {'name': filename,
             'type': 'binary',
             'public': False,
             'datas': out})
        if attachment_id:
            report = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment_id.id,
                'target': 'self',
            }
            return report
