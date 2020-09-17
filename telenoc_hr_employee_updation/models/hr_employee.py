# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    date_of_issue = fields.Date('Date of Issue')
    date_of_expiry = fields.Date('Date of Expiry')
    iqama_number = fields.Char('Iqama Number')
    iqama_date_of_issue = fields.Date('Date of Issue')
    iqama_date_of_expiry = fields.Date('Date of Expiry')
    bank_name = fields.Char('Bank Name')
    account_number = fields.Char('Account Number')
    iban_number = fields.Char('IBAN Number')
    employee_code = fields.Char()
