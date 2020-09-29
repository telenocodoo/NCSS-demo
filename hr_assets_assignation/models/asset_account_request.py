# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import datetime


class AssetAccountRequest(models.Model):
    _name = 'asset.account.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    def get_account_asset_assignation(self):
        asset_request_ids = self.search([('state', '=', 'assigned')]).mapped('asset_id').ids
        domain = [('state', '=', 'open'), ('id', 'not in', asset_request_ids)]
        return domain

    employee_id = fields.Many2one('hr.employee', 'Employee')
    type = fields.Selection([('asset', 'Asset'),
                             ('non_asset', 'Non Asset'),
                             ], default='asset', tracking=True)
    asset_id = fields.Many2one('account.asset', domain=get_account_asset_assignation)
    description = fields.Char()
    type_of_disclaimer = fields.Selection([('vacation', 'Vacation'),
                             ('final', 'Final'),
                             ('both', 'Both'),
                             ], default='vacation', tracking=True)
    date = fields.Date(default=fields.date.today())
    date_of_disclaimer = fields.Date('Date Of Clearance')
    is_disclaimer = fields.Boolean('Cleared')
    state = fields.Selection([('draft', 'Draft'),
                              ('assigned', 'Assigned'),
                              ('clearance', 'clearance'),
                              ], default='draft', tracking=True, )
    employee_asset_id = fields.Many2one('employee.assets')

    def action_assign_to_employee(self):
        self.state = 'assigned'

    def action_clearance(self):
        self.date_of_disclaimer = fields.date.today()
        self.state = 'clearance'

    def set_to_draft(self):
        self.state = 'draft'


class CustodyRequestLine(models.Model):
    _name = 'employee.assets'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    asset_account_ids = fields.One2many('employee.asset.line', 'employee_asset_id')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    type_of_disclaimer = fields.Selection([('vacation', 'Vacation'),
                                           ('final', 'Final'),
                                           ('both', 'Both'),
                                           ], default='vacation', tracking=True)
    description = fields.Text()
    state = fields.Selection([('draft', 'Draft'),
                              ('first_approve', 'Approve'),
                              ('clearance', 'clearance'),
                              ('done', 'Done'),
                              ], default='draft', tracking=True, )

    def action_first_approve(self):
        self.state = 'first_approve'

    def action_clearance(self):
        for record in self.asset_account_ids:
            if record.is_disclaimer:
                record.custody_request_id.action_clearance()
        self.state = 'clearance'

    def action_done(self):
        self.state = 'done'

    def set_to_draft(self):
        self.state = 'draft'

    @api.onchange('employee_id', 'type_of_disclaimer')
    def onchange_employee_id(self):
        self.asset_account_ids = False
        if self.employee_id:
            asset_account_obj = self.env['asset.account.request'].search([('employee_id.id', '=', self.employee_id.id),
                                                                          ('state', '=', 'assigned'),
                                                                          ('type_of_disclaimer', '=', self.type_of_disclaimer)])
            if asset_account_obj:
                for line in asset_account_obj:
                    self.asset_account_ids.new({
                        'employee_asset_id': self.id,
                        'employee_id': line.employee_id,
                        'custody_request_id': line.id,
                        'type': line.type,
                        'asset_id': line.asset_id.id,
                        'description': line.description,
                        'date': line.date,
                    })

    def get_day_name_from_date(self, contract_day):
        contract_day = str(contract_day)
        year, month, day = contract_day.split('-')
        day_name = datetime.date(int(year), int(month), int(day))
        e_name = day_name.strftime("%A")
        if e_name == 'Saturday':
            ar_name = 'السبت'
        elif e_name == 'Sunday':
            ar_name = 'الاحد'
        elif e_name == 'Monday':
            ar_name = 'الاثنين'
        elif e_name == 'Tuesday':
            ar_name = 'الثلاثاء'
        elif e_name == 'Wednesday':
            ar_name = 'الاربعاء'
        elif e_name == 'Thursday':
            ar_name = 'الخميس'
        else:
            ar_name = 'الجمعه'
        return ar_name


class EmployeeAssetLine(models.Model):
    _name = 'employee.asset.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    custody_request_id = fields.Many2one('asset.account.request')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    type = fields.Selection([('asset', 'Asset'),
                             ('non_asset', 'Non Asset'),
                             ], default='asset', tracking=True)
    asset_id = fields.Many2one('account.asset')
    description = fields.Char()
    type_of_disclaimer = fields.Selection([('vacation', 'Vacation'),
                             ('final', 'Final'),
                             ('both', 'Both'),
                             ], default='vacation', tracking=True)
    date = fields.Date(default=fields.date.today(), string='Assignation Date')
    date_of_disclaimer = fields.Date('Date Of Clearance')
    is_disclaimer = fields.Boolean('Cleared')
    employee_asset_id = fields.Many2one('employee.assets')