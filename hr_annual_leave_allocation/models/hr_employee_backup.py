from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    def unlink(self):
        leave_type_id = self.env.user.company_id.leave_type_id
        for record in self:
            if leave_type_id.id == record.id:
                raise UserError(_("You are not allowed to delete This record!!"))
        return super(HrLeaveType, self).unlink()


# class HrLeaveAllocation(models.Model):
#     _inherit = 'hr.leave.allocation'
#
#     employee_id = fields.Many2one(store=True)

    # @api.onchange('employee_id')
    # def onchange_employee_id2(self):
    #     for record in self:
    #         if record.employee_id:
    #             record.employee_id2 = record.employee_id
class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    last_allocation_date = fields.Date()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    join_date = fields.Date()
    working_date = fields.Date()
    last_allocation_date = fields.Date()
    allocation_ids = fields.One2many('hr.leave.allocation', 'employee_id')

    @api.model
    def cron_employee_annual_allocation(self):
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        allocation_obj = self.env['hr.leave.allocation']
        no_of_days_per_year = company.no_of_days_per_year
        allocation_type = company.allocation_type
        leave_type_id = company.leave_type_id
        leave_id = company.leave_id
        unpaid_type = company.unpaid_type
        first_period = company.first_period
        deserve_first_period = company.deserve_first_period
        second_period = company.second_period
        deserve_second_period = company.deserve_second_period
        leave_ids = self.env['hr.leave']
        employee_ids = self.env['hr.employee'].search([])
        # print(">>>>>>no_of_days_per_year>>>>", no_of_days_per_year)
        # print(">>>>>>company>>>>", company)
        # print(">>>>>>22222222222>>>>", employee_ids)
        for employee in employee_ids:
            if employee.last_allocation_date:
                allocation_per_days = (fields.date.today() - employee.last_allocation_date).days
                allocation_per_year = allocation_per_days / no_of_days_per_year
                allocation_per_month = allocation_per_days / 30
                if allocation_type == 'Yearly':
                    if allocation_per_year >= 1:

                elif allocation_type == 'Monthly':
                    if allocation_per_month >= 1:

                else:
            if employee.join_date:
                leave = 0.0
                total_work_days = 0.0
                deserve_period = 0.0
                final_period = 0.0
                total_days = (fields.date.today() - employee.join_date).days
                #how to get unpaid leaves ('holiday_status_id.name', '=', 'Unpaid')
                leave_obj_id = leave_ids.search([('employee_id', '=', employee.id),
                                             ('holiday_status_id', '=', leave_id.id)])
                if leave_obj_id:
                    for l in leave_obj_id:
                        leave += l.number_of_days

                if unpaid_type == 'Add':
                    total_work_days = total_days - leave
                else:
                    total_work_days = total_days
                no_of_years = total_work_days / no_of_days_per_year
                if no_of_years <= first_period: # less than 5 years
                    print("no_of_years", no_of_years)
                    # deserve_period = deserve_first_period
                    no_of_deserved_days = (fields.date.today() - employee.working_date).days
                    no_of_years_deserved = no_of_deserved_days / no_of_days_per_year #1.3 year
                    print("no_of_years_deserved", no_of_years_deserved)
                    day_per_year = deserve_first_period / no_of_days_per_year #21/365
                    print("day_per_year", day_per_year)

                    if allocation_type == 'Yearly':
                        deserve_period = no_of_years_deserved * deserve_first_period

                    elif allocation_type == 'Monthly':
                        deserve_period = no_of_years_deserved * (deserve_first_period / 12)

                    else:
                        deserve_period = no_of_years_deserved * day_per_year
                    #magdy
                    # if no_of_years_deserved >= 1:
                    #     print("111111111111111")
                    #     no_of_months_deserved = int(no_of_years_deserved)
                    #     print("no_of_months_deserved", no_of_months_deserved)
                    #     remain = no_of_years_deserved - no_of_months_deserved #3 months (90 days)
                    #     print("remain", remain)
                    #     if allocation_type in ['Daily', 'Monthly']:
                    #         remain_per_day = remain * 10 * 30 * day_per_year #3month * 30day * day_per_year
                    #         print("remain_per_day", remain_per_day)
                    #         deserve_period = (no_of_months_deserved * deserve_first_period) + remain_per_day
                    #         print("deserve_period", deserve_period)
                    #     else:
                    #         deserve_period = (no_of_months_deserved * deserve_first_period)
                    #         print("deserve_period", deserve_period)
                    # else: #have only 3 month
                    #     print("222222222222222222222")
                    #     if allocation_type in ['Daily', 'Monthly']:
                    #         print("222222222222222222222111111111")
                    #         remain_per_day = no_of_years_deserved * 30 * day_per_year  # 3month * 30day * day_per_year
                    #         print("remain_per_day", no_of_years_deserved * 30)
                    #         deserve_period = remain_per_day
                    #         print("deserve_period", deserve_period)
                    #         # deserve_period = (no_of_months_deserved * deserve_first_period) + remain_per_day
                    #magdy
                else:
                    print("no_of_years", no_of_years)
                    # deserve_period = deserve_first_period
                    no_of_deserved_days = (fields.date.today() - employee.working_date).days
                    no_of_years_deserved = no_of_deserved_days / no_of_days_per_year  # 1.3 year
                    print("no_of_years_deserved", no_of_years_deserved)
                    period_after_5_years = no_of_years - first_period #No of period after 5 years .3 month
                    print("period_after_5_years", period_after_5_years)
                    period_before_5_years = no_of_years_deserved - period_after_5_years #No of period before 5 years 1 year
                    print("period_before_5_years", period_before_5_years)
                    day_per_year_before_5 = deserve_first_period / no_of_days_per_year  # 21/365
                    day_per_year_after_5 = deserve_second_period / no_of_days_per_year  # 30/365
                    print("day_per_year_before_5", day_per_year_before_5)
                    print("day_per_year_after_5", day_per_year_after_5)

                    if period_before_5_years <= 0: #get allocation with 30 days
                        if allocation_type == 'Yearly':
                            deserve_period = no_of_years_deserved * deserve_second_period

                        elif allocation_type == 'Monthly':
                            deserve_period = no_of_years_deserved * (deserve_second_period / 12)

                        else:
                            deserve_period = no_of_years_deserved * day_per_year_after_5
                        #magdy
                        # if no_of_years_deserved >= 1: #1.3 year
                        #     print("111111111111111")
                        #     no_of_months_deserved = int(no_of_years_deserved) #1 year
                        #     print("no_of_months_deserved", no_of_months_deserved)
                        #     remain = no_of_years_deserved - no_of_months_deserved  # 3 months (90 days)
                        #     print("remain", remain)
                        #     if allocation_type in ['Daily', 'Monthly']:
                        #         remain_per_day = remain * 10 * 30 * day_per_year_after_5  # 3month * 30day * day_per_year
                        #         print("remain_per_day", remain_per_day)
                        #         deserve_period = (no_of_months_deserved * deserve_second_period) + remain_per_day
                        #         print("deserve_period", deserve_period)
                        #     else:
                        #         deserve_period = (no_of_months_deserved * deserve_second_period)
                        #         print("deserve_period", deserve_period)
                        # else:  # have only 3 month
                        #     print("222222222222222222222")
                        #     # if allocation_type in ['Daily', 'Monthly']:
                        #     #     print("222222222222222222222111111111")
                        #     remain_per_day = no_of_years_deserved * 30 * day_per_year_after_5  # 3month * 30day * day_per_year
                        #     print("remain_per_day", no_of_years_deserved * 30)
                        #     deserve_period = remain_per_day
                        #     print("deserve_period", deserve_period)
                        #magdy
                                # deserve_period = (no_of_months_deserved * deserve_first_period) + remain_per_day
                    else: #get allocation with 30 days and 21 days
                        t = 0.0
                        if period_before_5_years > 0:
                            if allocation_type == 'Yearly':
                                t = period_before_5_years * deserve_first_period

                            elif allocation_type == 'Monthly':
                                t = period_before_5_years * (deserve_first_period / 12)

                            else:
                                t = period_before_5_years * day_per_year_before_5
                        #magdy
                        # if period_before_5_years >= 1:
                        #     print("111111111111111")
                        #     no_of_months_deserved = int(period_before_5_years)
                        #     print("no_of_months_deserved", no_of_months_deserved)
                        #     remain = period_before_5_years - no_of_months_deserved  # 3 months (90 days)
                        #     print("remain", remain)
                        #     if allocation_type in ['Daily', 'Monthly']:
                        #         remain_per_day = remain * 10 * 30 * day_per_year_before_5  # 3month * 30day * day_per_year
                        #         print("remain_per_day", remain_per_day)
                        #         t = (no_of_months_deserved * deserve_first_period) + remain_per_day
                        #         print("deserve_period", t)
                        #     else:
                        #         t = (no_of_months_deserved * deserve_first_period)
                        #         print("deserve_period", t)
                        # else:  # have only 3 month
                        #     print("222222222222222222222")
                        #     if allocation_type in ['Daily', 'Monthly']:
                        #         print("222222222222222222222111111111")
                        #         remain_per_day = period_before_5_years * 10 * 30 * day_per_year_before_5  # 3month * 30day * day_per_year
                        #         # print("remain_per_day", period_before_5_years * 10 * 30)
                        #         t = remain_per_day
                        #         print("deserve_period", t)
                        #magdy
                        if period_after_5_years > 0:
                            if allocation_type == 'Yearly':
                                t += period_after_5_years * deserve_second_period

                            elif allocation_type == 'Monthly':
                                t += period_before_5_years * (deserve_second_period / 12)

                            else:
                                t += period_before_5_years * day_per_year_after_5
                        # magdy
                        # if period_after_5_years >= 1:
                        #     print("111111111111111")
                        #     no_of_months_deserved = int(period_after_5_years)
                        #     print("no_of_months_deserved", no_of_months_deserved)
                        #     remain = period_after_5_years - no_of_months_deserved  # 3 months (90 days)
                        #     print("remain", remain)
                        #     if allocation_type in ['Daily', 'Monthly']:
                        #         remain_per_day = remain * 10 * 30 * day_per_year_after_5  # 3month * 30day * day_per_year
                        #         print("remain_per_day", remain_per_day)
                        #         t += (no_of_months_deserved * deserve_second_period) + remain_per_day
                        #         print("deserve_period", t)
                        #     else:
                        #         t += (no_of_months_deserved * deserve_second_period)
                        #         print("deserve_period", t)
                        # else:  # have only 3 month
                        #     print("222222222222222222222")
                        #     # if allocation_type in ['Daily', 'Monthly']:
                        #     print("222222222222222222222111111111")
                        #     remain_per_day = period_after_5_years * 10 * 30 * day_per_year_after_5  # 3month * 30day * day_per_year
                        #     print("remain_per_day", period_after_5_years * 10 * 30)
                        #     t += remain_per_day
                        #     print("deserve_period", t)
                        # magdy
                        deserve_period = t
                # else:
                #     deserve_period = deserve_second_period
                # if allocation_type == 'Daily':
                #     final_period = deserve_period / no_of_days_per_year
                # elif allocation_type == 'Monthly':
                #     final_period = deserve_period / 12
                # else:
                final_period = deserve_period

                # print(">>>>>>leave>>>>", leave)
                # print(">>>>>>no_of_years>>>>", no_of_years)
                # print(">>>>>>total_work_days>>>>", total_work_days)
                print(">>>>>>employee>>>>", employee.name, employee.id)
                print(">>>>>>company>>>>", final_period)
                a = allocation_obj.create({
                    'name': 'Annual Allocation',
                    'holiday_status_id': leave_type_id.id,
                    'number_of_days': final_period,
                    'employee_id': employee.id,
                    'last_allocation_date': fields.Date.today(),
                })
                employee.last_allocation_date = fields.Date.today()
                print(a.id)