# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from datetime import datetime


class BudgetAllocatedTraining(models.Model):
    _name = 'budget.allocated.training'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "department_id"

    department_id = fields.Many2one('hr.department')
    budget = fields.Float()
    expensed_from_budget = fields.Float()
    remaining_from_budget = fields.Float(compute="compute_remaining_from_budget")
    start_date = fields.Date()
    end_date = fields.Date()

    @api.depends('budget','expensed_from_budget')
    def compute_remaining_from_budget(self):
        for record in self:
            record.remaining_from_budget = record.budget - record.expensed_from_budget


class CoursePlace(models.Model):
    _name = 'course.place'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    need_ticket = fields.Boolean(default=True)


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
    number_of_paid_courses_per_year = fields.Float()
    number_of_free_courses_per_year = fields.Float()
    allowed_period_between_courses = fields.Float()


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
    number_of_days = fields.Float()
    start_date = fields.Date()
    end_date = fields.Date()
    is_free = fields.Boolean()

    @api.constrains('start_date', 'end_date')
    def constrains_start_end_date(self):
        for record in self:
            if record.end_date < record.start_date:
                raise UserError(_("End Date Must Be Greater Than Start Date"))

    @api.onchange('start_date', 'end_date')
    def onchange_start_end_date(self):
        if self.start_date and self.end_date:
            date_format = "%Y-%m-%d"
            start_date = datetime.strptime(str(self.start_date), date_format)
            end_date = datetime.strptime(str(self.end_date), date_format)
            self.number_of_days = float((end_date-start_date).days)


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
    course_place_id = fields.Many2one('course.place')
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
    total = fields.Float(compute='get_total_expenses', store=True)
    Subsistence_rate = fields.Float()
    is_direct_manager = fields.Boolean(compute='get_direct_manager')
    is_department_manager = fields.Boolean(compute='compute_department_manager')
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
    color = fields.Integer(compute="compute_color")

    @api.depends('state')
    def compute_color(self):
        for record in self:
            if record.state == 'draft':
                record.color = 2
            elif record.state == 'direct_manager_approve':
                record.color = 4
            elif record.state == 'department_manager_approve':
                record.color = 6
            elif record.state == 'accounting_approve':
                record.color = 8
            else:
                record.color = 10

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.employee_degree_id = self.employee_id.employee_degree_id.id
        self.traveling_type = self.employee_id.employee_degree_id.traveling_type

    @api.onchange('course_id')
    def onchange_company_id(self):
        for record in self:
            if record.course_id:
                if not record.employee_id:
                    raise UserError(_("Please Add Employee"))
                record.description = record.course_id.description
                record.course_type = record.course_id.type
                record.price = record.course_id.price
                record.number_of_days = record.course_id.number_of_days
                record.description = record.course_id.description
                course_obj = self.search(
                    [('employee_id', '=', self.employee_id.id), ('state', '=', 'accounting_approve')])
                if course_obj:
                    print(">>>>>>>>>>>>>>>>.", course_obj[-1])
                    print(">>>>>>>>>>>>>>>>.", course_obj)
                    start_year = date(self.course_id.end_date.year, 1, 1)
                    end_year = date(self.course_id.end_date.year, 12, 31)
                    print("start_year", self.course_id.end_date)
                    print("start_year", start_year)
                    print("end_year", end_year)
                    courses_approved_within_year = self.search_count([('employee_id', '=', self.employee_id.id),
                                                                     ('state', '=', 'accounting_approve'),
                                                                     ('course_id.end_date', '>=', start_year),
                                                                     ('course_id.end_date', '<=', end_year),
                                                                     ('course_id.is_free', '=', self.course_id.is_free),
                                                                     ])
                    print("self.course_id.is_free", self.course_id.is_free)
                    print("courses_approved_within_year", courses_approved_within_year)
                    if self.course_id.is_free:
                        if courses_approved_within_year >= self.employee_degree_id.number_of_free_courses_per_year:
                            print("111111111111111111111")
                            raise UserError(_("You aren't allowed to Request Extra Free Courses "
                                              "The Number Of Courses "
                                              "Allowed For "
                                              "You Is"
                                              " %s" % self.employee_degree_id.number_of_free_courses_per_year))
                    else:
                        if courses_approved_within_year >= self.employee_degree_id.number_of_paid_courses_per_year:
                            print("2222222222222222222")
                            raise UserError(_("You aren't allowed to Request Extra Paid Courses "
                                              "The Number Of Courses "
                                              "Allowed For "
                                              "You Is"
                                              " %s" % self.employee_degree_id.number_of_paid_courses_per_year))
                    date_format = "%Y-%m-%d"
                    last_course_end_date = datetime.strptime(str(course_obj[-1].course_id.end_date), date_format)
                    current_course_start_date = datetime.strptime(str(self.course_id.start_date), date_format)
                    difference_between_last_two_courses = float((current_course_start_date - last_course_end_date).days)

                    print("last_course_date", last_course_end_date)
                    print("current_course_date", current_course_start_date)
                    print("difference_between_last_two_courses", difference_between_last_two_courses)
                    print("allowed_period_between_courses", self.employee_degree_id.allowed_period_between_courses)
                    if difference_between_last_two_courses < self.employee_degree_id.allowed_period_between_courses:
                        raise UserError(_("You aren't allowed to Request Extra Course "
                                          "last course you take at %s" % course_obj[-1].course_id.end_date))

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
                    self.is_direct_manager = True
                else:
                    self.is_direct_manager = False
            else:
                self.is_direct_manager = False

    def compute_department_manager(self):
        current_user_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).id
        for record in self:
            if record.employee_id.department_id and record.employee_id.department_id.manager_id:
                if record.employee_id.department_id.manager_id.id == current_user_id:
                    budget_obj = self.env['budget.allocated.training'].search(
                        [('department_id.id', '=', record.employee_id.department_id.id)], limit=1)
                    if budget_obj:
                        if budget_obj.remaining_from_budget > record.total:
                            self.is_department_manager = True
                        else:
                            self.is_department_manager = False
                    else:
                        self.is_department_manager = False
                else:
                    self.is_department_manager = False
            else:
                self.is_department_manager = False

    def action_direct_manager_approve(self):
        self.state = 'direct_manager_approve'

    def action_department_manager_approve(self):
        for record in self:
            budget_obj = self.env['budget.allocated.training'].search(
                [('department_id.id', '=', record.employee_id.department_id.id)], limit=1)
            if budget_obj:
                budget_obj.expensed_from_budget += record.total
            record.state = 'department_manager_approve'

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
