# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeDegreeValue(models.Model):
    _name = 'employee.degree.value'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    internal_day_value = fields.Float()
    external_day_value = fields.Float()
    traveling_type = fields.Selection([('tourism', 'tourism'),
                                       ('first_class', 'First Class'),
                                       ('vip', 'VIP'),
                                       ])


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    employee_degree_id = fields.Many2one('employee.degree.value')


class TrainingCourse(models.Model):
    _name = 'training.course'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char()
    description = fields.Text()
    type = fields.Selection([('internal', 'Internal'), ('external', 'External')])
    price = fields.Float()
    number_of_days = fields.Integer()


class MandatePassenger(models.Model):
    _name = 'mandate.passenger'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    employee_type = fields.Selection([('employee', 'Employee'),
                                      ('department_manager', 'Department Manager'),
                                      ('manager', 'Manager'),
                                      ])
    employee_degree_id = fields.Many2one('employee.degree.value')
    type = fields.Selection([('course', 'Course'),
                              ('mandate', 'Mandate'),
                              ('work_shop', 'work shop'),
                              ])
    course_id = fields.Many2one('training.course', 'Course')
    course_type = fields.Selection([('internal', 'Internal'), ('external', 'External')])
    description = fields.Text()
    price = fields.Float()
    number_of_days = fields.Integer()
    total_value_without_ticket = fields.Float(compute='get_total_value_without_ticket')
    day_value = fields.Float(compute='get_total_value')
    housing_value = fields.Float(compute='get_total_value')
    transportation_value = fields.Float(compute='get_total_value')
    daily_expenses = fields.Float(compute='get_total_value')
    total = fields.Float(compute='get_total_expenses')
    Subsistence_rate = fields.Float()
    is_direct_manager = fields.Boolean(compute='get_direct_manager')
    traveling_type = fields.Selection([('tourism', 'tourism'),
                                       ('first_class', 'First Class'),
                                       ('vip', 'VIP'),
                                       ])
    reason = fields.Text()
    state = fields.Selection([('draft', 'Draft'),
                               ('direct_manager_approve', 'Direct Manager Approve'),
                               ('department_manager_approve', 'Department Manager Approve'),
                               ('accounting_approve', 'Accounting Approve'),
                               ('refuse', 'Refuse'),
                               ], default='draft')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.employee_degree_id = self.employee_id.employee_degree_id.id
        self.traveling_type = self.employee_id.employee_degree_id.traveling_type

    @api.onchange('course_id')
    def onchange_company_id(self):
        for record in self:
            if record.course_id:
                record.description = record.course_id.description
                record.course_type = record.course_id.type
                record.price = record.course_id.price
                record.number_of_days = record.course_id.number_of_days
                record.description = record.course_id.description

    @api.depends('employee_degree_id', 'course_type', 'number_of_days')
    def get_total_value_without_ticket(self):
        for record in self:
            if record.course_type == 'internal':
                if record.employee_degree_id:
                   record.total_value_without_ticket = record.employee_degree_id.internal_day_value * record.number_of_days
            elif record.course_type == 'external':
                if record.employee_degree_id:
                    record.total_value_without_ticket = record.employee_degree_id.external_day_value * record.number_of_days
            else:
                record.total_value_without_ticket = 0.0

    @api.depends('total_value_without_ticket', 'number_of_days')
    def get_total_value(self):
        for record in self:
            if record.total_value_without_ticket > 0.0 and record.number_of_days > 0.0:
                record.day_value = record.total_value_without_ticket / record.number_of_days
                record.housing_value = (record.total_value_without_ticket*50)/100
                record.transportation_value = (record.total_value_without_ticket*25)/100
                record.daily_expenses = (record.total_value_without_ticket*25)/100
            else:
                record.day_value = 0.0
                record.housing_value = 0.0
                record.transportation_value = 0.0
                record.daily_expenses = 0.0

    @api.depends('total_value_without_ticket', 'price')
    def get_total_expenses(self):
        for record in self:
            record.total = record.total_value_without_ticket + record.price

    def get_direct_manager(self):
        current_user_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).id
        for record in self:
            if record.employee_id and record.employee_id.parent_id:
                if record.employee_id.parent_id.id == current_user_id:
                    print(record.employee_id.parent_id.name)
                    print(record.employee_id.parent_id.id)
                    print(current_user_id)
                    self.is_direct_manager = True
                else:
                    self.is_direct_manager = False
            else:
                self.is_direct_manager = False
            # employee_ids = self.env['hr.employee'].search([('parent_id.id', '=', current_user_id)])
            # print(record.employee_id.name)
            # print(record.employee_id.parent_id.name)
            # self.is_direct_manager = True

    def action_direct_manager_approve(self):
        self.state = 'direct_manager_approve'

    def action_department_manager_approve(self):
        self.state = 'department_manager_approve'

    def action_accounting_approve(self):
        self.state = 'accounting_approve'

    def refuse_action(self):
        for record in self:
            if not record.reason:
                raise UserError(_("Please Add the reason of Refuse"))
            else:
                self.state = 'refuse'

    def set_to_draft(self):
        self.state = 'draft'
