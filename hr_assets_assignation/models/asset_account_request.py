# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class carfleetvicle(models.Model):
    _inherit = 'fleet.vehicle'
    history_count_emp = fields.Integer(compute="_compute_count_all_emp", string="Employees History Count")
    is_take_by_employee = fields.Boolean(  string="Is Taken", default=False)

    def _compute_count_all_emp(self):

        for record in self:
           record.history_count_emp = self.env['fleet.vehicle.employee.log'].search_count([('vehicle_id', '=', record.id)])



    def open_fleet_employee_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignation Logs',
            'view_mode': 'tree',
            'res_model': 'fleet.vehicle.employee.log',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_driver_id': self.driver_id.id, 'default_vehicle_id': self.id}
        }
class Cardriverdetails(models.Model):

    _name = "fleet.vehicle.employee.log"
    _description = "Drivers history on a vehicle"
    _order = "create_date desc, date_start desc"
    _rec_name = "driver_id"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True,domain="[('is_take_by_employee','=',False)]")
    driver_id = fields.Many2one('hr.employee', string="Driver", required=True)
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    state_of_asset_when_receive = fields.Char()
    state_of_asset_when_delivery = fields.Char()


class AssetAccountRequest(models.Model):
    _name = 'asset.account.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    def get_account_asset_assignation(self):
        asset_request_ids = self.search([('state', '=', 'assigned')]).mapped('asset_id').ids
        domain = [('state', '=', 'open'), ('id', 'not in', asset_request_ids)]
        return domain

    def get_employee_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if employee_id:
            return employee_id.id
        else:
            return False

    asset_request_description = fields.Char()
    asset_request_Refuse_reason = fields.Char(string="Refuse Reason")
    refuse_boolean=fields.Boolean(default=False)
    employee_id = fields.Many2one('hr.employee', 'Employee', default=get_employee_id)
    type = fields.Selection([('asset', 'Asset'),
                             ('non_asset', 'Non Asset'),
                             ], default='asset', tracking=True)
    asset_id = fields.Many2one('account.asset', string="Asset Name", domain=get_account_asset_assignation)
    description = fields.Char()
    type_of_disclaimer = fields.Selection([('vacation', 'Vacation'),
                                         ('final', 'Final'),
                                         ('both', 'Both'),
                                         ('at_specific_date', 'At Specific Date'),
                                         ], default='at_specific_date', tracking=True)
    date_of_asset_delivery = fields.Date(default=fields.date.today())
    date = fields.Date(default=fields.date.today())
    date_of_disclaimer = fields.Date('Date Of Clearance')
    is_disclaimer = fields.Boolean('Cleared')
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('approve', 'In progress'),
                              ('assigned', 'Assigned'),
                              ('clearance', 'clearance'),
                              ('refuse', 'Refused'),
                              ], default='draft', tracking=True, )
    employee_asset_id = fields.Many2one('employee.assets')
    color = fields.Integer(compute="compute_color")
    state_of_asset_when_receive = fields.Char()
    state_of_asset_when_delivery = fields.Char()
    log_id_employee= fields.Many2one('fleet.vehicle.employee.log',string=_("Employee Car"))


    # def _get_car(self):
    #     if self.asset_id.car_ids:
    #        return self.asset_id.car_ids.id

    car_employee_have= fields.Many2one('fleet.vehicle',string=_("Employee Car"),readonly=True )
    is_car=fields.Boolean("Car",default=False)

    @api.onchange('asset_id')
    def _getCar(self):
        print("tesr>>>")
        if self.asset_id.car_ids:
            self.car_employee_have=self.asset_id.car_ids.id
            self.is_car=True
        else:
            self.is_car = False
            self.car_employee_have=False
            self.log_id_employee=False


    #        return self.asset_id.car_ids.id

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user.has_group('hr_assets_assignation.asset_assignation_user')
        direct_manager = self.env.user.has_group('hr_assets_assignation.asset_assignation_direct_manager')
        department_manager = self.env.user.has_group('hr_assets_assignation.asset_assignation_department_manager')
        center_manager = self.env.user.has_group('hr_assets_assignation.asset_assignation_center_manager')
        current_user_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).id

        if center_manager:
            args += []
        elif department_manager:
            args += ['|', '|', ('employee_id', '=', current_user_id),
                     ('employee_id.department_id.manager_id.id', '=', current_user_id),
                     ('create_uid.id', '=', self.env.user.id)]
        elif direct_manager:
            args += ['|', '|', ('employee_id', '=', current_user_id),
                     ('employee_id.parent_id.id', '=', current_user_id), ('create_uid.id', '=', self.env.user.id)]
        elif user:
            args += ['|', ('employee_id', '=', current_user_id), ('create_uid', '=', self.env.user.id)]


        return super(AssetAccountRequest, self).search(args=args, offset=offset, limit=limit, order=order, count=count)

    @api.depends('state')
    def compute_color(self):
        for record in self:
            if record.state == 'draft':
                record.color = 2
            elif record.state == 'assigned':
                record.color = 4
            else:
                record.color = 6

    def action_submit(self):
        self.state = 'submit'

    def action_approve(self):
        self.state = 'approve'

    def action_refuse(self):

        self.state = 'refuse'


    def action_assign_to_employee(self):
        now = datetime.now()

        values={}
        if self.asset_id.car_ids.id:
            values['driver_id']=self.employee_id.id
            values['date_start']=now
            values['state_of_asset_when_receive']=self.state_of_asset_when_receive
            values['vehicle_id']=self.asset_id.car_ids.id
            self.asset_id.car_ids.is_take_by_employee=True
            log_id=self.env['fleet.vehicle.employee.log'].sudo().create(values)
            self.log_id_employee = log_id
        self.state = 'assigned'

    def action_clearance(self):
        now = datetime.now()
        # self.env['fleet.vehicle.assignation.log'].sudo().create(driver_id=self.employee_id, date_start=now,
        #  state_of_asset_when_receive=self.state_of_asset_when_receive)
        print(self.log_id_employee.id)
        log_id=self.env['fleet.vehicle.employee.log'].sudo().search([('id','=', self.log_id_employee.id)  ],limit=1)
        print(" hi .???",log_id)
        if len(log_id)==1:
            now = datetime.now()
            values = {}
            values['date_end'] = now
            values['state_of_asset_when_delivery'] = self.state_of_asset_when_delivery
            # values['vehicle_id'] = self.asset_id.car_ids.id
            # self.asset_id.car_ids.is_take_by_employee = True
            print(values)
            for rec in log_id:
                print(log_id)
                rec.write(values)

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
                              ('first_approve', 'Request Sent'),
                              ('clearance', 'clearance'),
                              ], default='draft', tracking=True, )
    # ('done', 'Done'),
    color = fields.Integer(compute="compute_color")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        employee = self.env.user.has_group('hr_assets_assignation.employee_asset_user')
        direct_manager = self.env.user.has_group('hr_assets_assignation.employee_asset_direct_manager')
        department_manager = self.env.user.has_group('hr_assets_assignation.employee_asset_department_manager')
        center_manager = self.env.user.has_group('hr_assets_assignation.employee_asset_center_manager')
        current_user_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).id

        if employee:
            args += ['|', ('employee_id', '=', current_user_id), ('create_uid', '=', self.env.user.id)]
        if direct_manager:
            args += ['|', '|', ('employee_id', '=', current_user_id),
                     ('employee_id.parent_id.id', '=', current_user_id), ('create_uid.id', '=', self.env.user.id)]
        if department_manager:
            args += ['|', '|', ('employee_id', '=', current_user_id),
                     ('employee_id.department_id.manager_id.id', '=', current_user_id),
                     ('create_uid.id', '=', self.env.user.id)]
        if center_manager:
            args += []
        return super(CustodyRequestLine, self).search(args=args, offset=offset, limit=limit, order=order, count=count)

    @api.depends('state')
    def compute_color(self):
        for record in self:
            if record.state == 'draft':
                record.color = 2
            elif record.state == 'first_approve':
                record.color = 4
            elif record.state == 'clearance':
                record.color = 6
            else:
                record.color = 8

    def action_first_approve(self):
        for record in self:
            items_need_disclaimer = record.asset_account_ids.filtered(lambda l: l.is_disclaimer == False)
            if len(items_need_disclaimer) >= len(record.asset_account_ids):
                raise UserError(_("You Must Select At Least One Asset To Approve"))
            record.state = 'first_approve'

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


class DepartmentClearance(models.Model):
    _name = 'department.clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    department_clearance_line_ids = fields.One2many('department.clearance.line', 'department_clearance_id')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.department_clearance_line_ids = False
        if self.employee_id:
            department_obj = self.env['hr.department'].search([])
            if department_obj:
                for line in department_obj:
                    self.department_clearance_line_ids.new({
                        'department_clearance_id': self.id,
                        'department_id': line.id,
                        'department_manager_id': line.manager_id.id,
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


class DepartmentClearanceLine(models.Model):
    _name = 'department.clearance.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    department_clearance_id = fields.Many2one('department.clearance')
    department_id = fields.Many2one('hr.department', 'Department Name')
    department_manager_id = fields.Many2one('hr.employee')
    notes = fields.Char()
    signature = fields.Char()
    date = fields.Date('Clearance Date', default=fields.date.today())
    is_department_manager = fields.Boolean(compute="compute_is_department_manager")

    @api.onchange('department_id')
    def onchange_department_id(self):
        for record in self:
            record.department_manager_id = record.department_id.manager_id.id

    @api.depends('department_manager_id')
    def compute_is_department_manager(self):
        for record in self:
            current_user_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if current_user_id:
                if current_user_id.department_id and current_user_id.department_id.manager_id:
                    if record.department_manager_id.id == current_user_id.department_id.manager_id.id:
                        record.is_department_manager = True
                    else:
                        record.is_department_manager = False
                else:
                    record.is_department_manager = False
            else:
                record.is_department_manager = False

class AssetAccount(models.Model):

    _inherit = 'account.asset'

    car_ids = fields.Many2one('fleet.vehicle',string =_('Cars '))
