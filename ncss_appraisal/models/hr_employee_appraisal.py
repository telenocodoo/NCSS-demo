# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class HrEmployeeAppraisalType(models.Model):
    _name = 'hr.employee.appraisal.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()


class AppraisalRecommendations(models.Model):
    _name = 'appraisal.recommendations'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    is_default = fields.Boolean('Default recommendations')
    appraisal_type_id = fields.Many2one('hr.employee.appraisal.type')


class AppraisalManagerRecommendations(models.Model):
    _name = 'appraisal.manager.recommendations'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    appraisal_manager_recommendations_id = fields.Many2one('hr.employee.appraisal')
    appraisal_recommendation_id = fields.Many2one('appraisal.recommendations')
    approve_recommendation = fields.Boolean('Yes')
    disagree_recommendation = fields.Boolean('No')


class StrongWeakPointLines(models.Model):
    _name = 'strong.weak.point.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    strong_weak_point_lines_id = fields.Many2one('hr.employee.appraisal')
    strong_points = fields.Char()
    weak_points = fields.Char()


class AppraisalLevel(models.Model):
    _name = 'appraisal.level'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()


class AppraisalCriteria(models.Model):
    _name = 'appraisal.criteria'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    max_limit = fields.Float()
    is_default = fields.Boolean('Default Criteria')
    appraisal_type_id = fields.Many2one('hr.employee.appraisal.type')


class AppraisalItem(models.Model):
    _name = 'appraisal.item'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    hr_employee_appraisal_id = fields.Many2one('hr.employee.appraisal')
    appraisal_criteria_id = fields.Many2one('appraisal.criteria')
    max_limit = fields.Float()
    deserved_degree = fields.Float()
    appraisal_level = fields.Char(compute='compute_appraisal_level')
    appraisal_level_id = fields.Many2one('appraisal.level')

    @api.onchange('deserved_degree')
    def onchange_deserved_degree(self):
        for record in self:
            if record.deserved_degree > record.max_limit:
                raise UserError(_("Deserve degree must be less than maximum limit"))

    @api.onchange('deserved_degree', 'max_limit')
    def compute_appraisal_level(self):
        for record in self:
            if record.deserved_degree and record.max_limit:
                result = (record.deserved_degree / record.max_limit)*100
                print("::::::::::::::result : ", result)
                if result <= 50:
                    record.appraisal_level = 'ضعيف'
                elif 50 < result <= 65:
                    record.appraisal_level = 'مقبول'
                elif 65 < result <= 75:
                    record.appraisal_level = 'جيد'
                elif 75 < result <= 89:
                    record.appraisal_level = 'عالي / جيد جداً'
                else:
                    record.appraisal_level = 'متميز / ممتاز'
            else:
                record.appraisal_level = ' '


class AdministrativeCommunication(models.Model):
    _name = 'hr.employee.appraisal'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee')
    manager_id = fields.Many2one('hr.employee')
    appraisal_id = fields.Many2one('hr.appraisal')
    appraisal_item_ids = fields.One2many('appraisal.item', 'hr_employee_appraisal_id', copy=True)
    strong_weak_point_ids = fields.One2many('strong.weak.point.lines', 'strong_weak_point_lines_id', copy=True)
    appraisal_manager_recommendations_ids = fields.One2many('appraisal.manager.recommendations',
                                                            'appraisal_manager_recommendations_id', copy=True)
    total_deserve_appraisal = fields.Float(compute='compute_total_deserve_appraisal')
    total_maximum_limit = fields.Float(compute='compute_total_deserve_appraisal')
    appraisal_level = fields.Char(compute='compute_appraisal_level')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('completed', 'Completed'),
                                        ], default='draft')

    @api.onchange('total_deserve_appraisal', 'total_maximum_limit')
    def compute_appraisal_level(self):
        for record in self:
            if record.total_deserve_appraisal and record.total_maximum_limit:
                result = (record.total_deserve_appraisal / record.total_maximum_limit) * 100
                print("::::::::::::::result : ", result)
                if result <= 50:
                    record.appraisal_level = 'ضعيف'
                elif 50 < result <= 65:
                    record.appraisal_level = 'مقبول'
                elif 65 < result <= 75:
                    record.appraisal_level = 'جيد'
                elif 75 < result <= 89:
                    record.appraisal_level = 'عالي / جيد جداً'
                else:
                    record.appraisal_level = 'متميز / ممتاز'
            else:
                record.appraisal_level = ' '

    def make_notification(self, message, employee):
        now = datetime.now()
        start_date = now.date()
        end_date = start_date + timedelta(days=1)
        notify_id = self.env['hr.notification'].sudo().create({'notification_MSG': message,
                                                               'date_start': start_date,
                                                               'date_end': end_date,
                                                               'state': 'notify',
                                                               'employee_id': employee})
        print("notify_id", notify_id)

    def action_complete_appraisal(self):
        low_deserve_degree = self.appraisal_item_ids.filtered(lambda r: r.deserved_degree == 0)
        if low_deserve_degree:
            raise UserError(_("Deserved Degree In Appraisal Criteria Must Be Bigger Than Zero"))

        self.state = 'completed'

        message = "تم الانتهاء من التقييم الخاص بك من %s" % self.manager_id.name
        self.make_notification(message, self.employee_id.id)

        activity_obj = self.env['mail.activity'].sudo().search([('res_id', '=', self.id),
                                                                ('user_id', '=', self.manager_id.user_id.id)])
        if activity_obj:
            # for act in activity_obj:
            #     print("LLLLLLLLL", act)
            activity_obj.sudo().action_done()

    @api.depends('appraisal_item_ids')
    def compute_total_deserve_appraisal(self):
        for record in self:
            record.total_deserve_appraisal = sum([line.deserved_degree for line in record.appraisal_item_ids])
            record.total_maximum_limit = sum([line.max_limit for line in record.appraisal_item_ids])
