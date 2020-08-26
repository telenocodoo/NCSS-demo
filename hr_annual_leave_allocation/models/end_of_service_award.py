# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EndOfServiceAward(models.Model):
    _name = 'end.of.service.award'
    _description = 'End of Service Award'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, index=True, tracking=True,
                                  track_visibility='onchange')
    contract_id = fields.Many2one('hr.contract', string='Contract', domain="[('employee_id', '=', employee_id)]",
                                  tracking=True, copy=False, related='employee_id.contract_id')
    join_date = fields.Date(string="Join Date", related='employee_id.join_date', tracking=True)
    last_work_date = fields.Date(tracking=True)
    contact_end_type = fields.Selection([('end_period', 'End of Contract Period'),
                                         ('immediate_resignation', 'Immediate resignation'),
                                         ('resignation_after_month', 'Resignation After Month'),
                                         ('law_80', 'Law 80'),
                                         ('law_77_by_employee', 'Law 77 By Employee'),
                                         ('law_77_by_company', 'Law 77 By Company'),
                                         ],
                                        default='end_period', tracking=True)

    number_of_days_from_join_date = fields.Integer(string="Number of Days From Join Date",
                                                   compute='_compute_number_of_days_from_join_date', tracking=True)
    total_unpaid_days = fields.Integer(compute='_compute_total_unpaid_days')
    net_period = fields.Integer(compute='_compute_all_net_period')
    total_days_before = fields.Float(string="Total Years Before Five Years", compute='_compute_total_years')
    total_days_after = fields.Float(string="Total Years After Five Years", compute='_compute_total_years')
    net_period_before_5year = fields.Float(string="Deserve First Period", compute='_compute_total_years')
    net_period_after_5year = fields.Float(string="Deserve Second Period", compute='_compute_total_years')
    final_deserving = fields.Float(string="Final Deserving", compute='_compute_final_deserving')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved')
    ], string='Status', readonly=True, tracking=True, copy=False, default='draft')

    def get_employee_end_of_service(self, employee_id, last_work_date, contact_end_type):
        employee_id = employee_id
        last_work_date = last_work_date
        contact_end_type = contact_end_type
        join_date = employee_id.join_date
        wage = employee_id.contract_id.wage
        leave = 0.0
        total_unpaid_days = 0.0
        number_of_days_from_join_date = 0.0
        net_period = 0.0
        total_years = 0.0
        total_days_before = 0.0
        net_period_before_5year = 0.0
        total_days_after = 0.0
        net_period_after_5year = 0.0
        final_deserving = 0.0
        # for rec in self:
        leave_ids = self.env['hr.leave']
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        leave_id = company.leave_id
        no_of_days_per_year = company.no_of_days_per_year
        first_period = company.first_period
        leave_obj_id = leave_ids.search([('employee_id', '=', employee_id.id),
                                         ('holiday_status_id', '=', leave_id.id)])
        if leave_obj_id:
            for l in leave_obj_id:
                leave += l.number_of_days
            total_unpaid_days = leave
        print("total_unpaid_days", total_unpaid_days)
        if last_work_date and join_date:
            difference_between_days = last_work_date - join_date
            number_of_days_from_join_date = difference_between_days.days
        print("number_of_days_from_join_date", number_of_days_from_join_date)
        net_period = number_of_days_from_join_date - total_unpaid_days
        print("net_period", net_period)
        total_years = net_period / no_of_days_per_year
        if total_years <= first_period:
            total_days_before = total_years
            net_period_before_5year = total_years * 15
            total_days_after = 0.0
            net_period_after_5year = 0.0
        else:
            total_days_before = first_period
            net_period_before_5year = first_period * 15
            total_days_after = total_years - first_period
            net_period_after_5year = self.total_days_after * 30
        print("total_days_before", total_days_before)
        print("net_period_before_5year", net_period_before_5year)
        print("total_days_after", total_days_after)
        print("net_period_after_5year", net_period_after_5year)
        total = 0.0
        if contact_end_type == 'end_period':
            total = net_period_before_5year + net_period_after_5year
        elif contact_end_type in ['immediate_resignation', 'resignation_after_month']:
            if total_years < 2:
                total = 0.0
            elif 2 <= total_years < 5:
                total = (net_period_before_5year + net_period_after_5year) / 3
            elif 5 <= total_years < 10:
                total = (net_period_before_5year + net_period_after_5year) * (2 / 3)
            else:
                total = (net_period_before_5year + net_period_after_5year)
        else:
            total = 0.0
        final_deserving = total
        deserving = final_deserving * wage / 30
        print("final_deserving", final_deserving)
        print("wage", wage)
        print("deserving", deserving)
        vals= {
            'join_date': join_date,
            'total_unpaid_days': total_unpaid_days,
            'number_of_days_from_join_date': number_of_days_from_join_date,
            'net_period': net_period,
            'total_days_before': total_days_before,
            'net_period_before_5year': net_period_before_5year,
            'total_days_after': total_days_after,
            'net_period_after_5year': net_period_after_5year,
            'final_deserving': final_deserving,
            'wage': wage,
            'deserving': deserving,
        }
        print("vals", vals)
        return vals

    @api.depends('employee_id')
    def _compute_total_unpaid_days(self):
        leave = 0.0
        for rec in self:
            if rec.employee_id:
                leave_ids = self.env['hr.leave']
                company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
                leave_id = company.leave_id
                leave_obj_id = leave_ids.search([('employee_id', '=', rec.employee_id.id),
                                                 ('holiday_status_id', '=', leave_id.id)])
                if leave_obj_id:
                    for l in leave_obj_id:
                        leave += l.number_of_days
        self.total_unpaid_days = leave

    @api.depends('join_date', 'last_work_date')
    def _compute_number_of_days_from_join_date(self):
        for record in self:
            record.number_of_days_from_join_date = 0
            if record.last_work_date and record.join_date:
                number_of_days_from_join_date = record.last_work_date - record.join_date
                record.number_of_days_from_join_date = number_of_days_from_join_date.days

    @api.depends('number_of_days_from_join_date', 'total_unpaid_days')
    def _compute_all_net_period(self):
        for record in self:
            record.net_period = record.number_of_days_from_join_date - record.total_unpaid_days

    @api.depends('net_period')
    def _compute_total_years(self):
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        no_of_days_per_year = company.no_of_days_per_year
        first_period = company.first_period
        total_years = 0.0
        total_days_before = 0.0
        total_days_after = 0.0
        for record in self:
            total_years = record.net_period / no_of_days_per_year
        if total_years <= first_period:
            self.total_days_before = total_years
            self.net_period_before_5year = total_years * 15
            self.total_days_after = 0.0
            self.net_period_after_5year = 0.0
        else:
            self.total_days_before = first_period
            self.net_period_before_5year = first_period * 15
            self.total_days_after = total_years - first_period
            self.net_period_after_5year = self.total_days_after * 30

    @api.depends('net_period_before_5year', 'net_period_after_5year', 'contact_end_type', 'net_period')
    def _compute_final_deserving(self):
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        no_of_days_per_year = company.no_of_days_per_year
        total_years = self.net_period / no_of_days_per_year
        total = 0.0
        for record in self:
            if record.contact_end_type == 'end_period':
                total = record.net_period_before_5year + record.net_period_after_5year
            elif record.contact_end_type in ['immediate_resignation', 'resignation_after_month']:
                if total_years < 2:
                    total = 0.0
                elif 2 <= total_years < 5:
                    total = (record.net_period_before_5year + record.net_period_after_5year)/3
                elif 5 <= total_years < 10:
                    total = (record.net_period_before_5year + record.net_period_after_5year) * (2/3)
                else:
                    total = (record.net_period_before_5year + record.net_period_after_5year)
            else:
                total = 0.0
        self.final_deserving = total

    def action_approve(self):
        self.get_employee_end_of_service(self.employee_id, self.last_work_date, self.contact_end_type)
        self.state = "approved"

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('You Can Not Delete a Request Which Is Not Draft.'))
            res = super(EndOfServiceAward, record).unlink()
            return res
