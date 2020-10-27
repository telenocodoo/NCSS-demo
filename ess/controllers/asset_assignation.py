# -*- coding: utf-8 -*-

import base64

from odoo.http import content_disposition, Controller, request, route
import odoo.addons.portal.controllers.portal as PortalController
from datetime import date, datetime
import base64
import io
from werkzeug.utils import redirect
from odoo import http
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo.tools.translate import _
import pytz
import time
from odoo.tools import formataddr

from .main import ESSPortal
# from odoo.addons.ess.controllers.main import ESSPortal


class EssAsset(Controller):

    # def check_modules(self):
    #     values = {}
    #     if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_announcement')]).state == 'installed':
    #         values.update({
    #             'announcement': True,
    #         })
    #     else:
    #         values.update({
    #             'announcement': False,
    #         })
    #     return values

    @route(['/request/asset'], type='http', auth='user', website=True)
    def asset(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        if post and request.httprequest.method == 'POST':
            post.update({
                'employee_id': emb_obj.id,
                'asset_request_description': post['description'],
            })

            asset_obj = request.env['asset.account.request'].sudo().create(post)
            asset_obj.sudo().action_submit()

            emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
            asset_assignation_obj = request.env['asset.account.request'].sudo().search(
                [('employee_id', '=', emb_obj.id)])

            values.update({
                'partner': request.env.user.partner_id,
                'employee': emb_obj,
                'asset_assignation_obj': asset_assignation_obj,
            })
            return request.render("ess.ess_view_asset_assignation", values)
        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
        })
        response = request.render("ess.ess_asset_assignation", values)
        return response

    @route(['/my/asset_assignation'], type='http', auth='user', website=True)
    def asset_assignation(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        asset_assignation_obj = request.env['asset.account.request'].sudo().search([('employee_id', '=', emb_obj.id)])

        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
            'asset_assignation_obj': asset_assignation_obj,
        })
        response = request.render("ess.ess_view_asset_assignation", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/custody/request'], type='http', auth='user', website=True)
    def custody(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        if post and request.httprequest.method == 'POST':
            post.update({
                'employee_id': emb_obj.id,
                'date': post['date'],
                'amount': post['amount'],
                'description': post['description'],
            })
            request.env['custody.request'].sudo().create(post)
            emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
            custody_obj = request.env['custody.request'].sudo().search([('employee_id', '=', emb_obj.id)])

            values.update({
                'partner': request.env.user.partner_id,
                'employee': emb_obj,
                'custody_obj': custody_obj,
            })
            return request.render("ess.ess_view_custody", values)
        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
        })
        response = request.render("ess.ess_custody_request", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/custody'], type='http', auth='user', website=True)
    def view_custody(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        custody_obj = request.env['custody.request'].sudo().search([('employee_id', '=', emb_obj.id)])

        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
            'custody_obj': custody_obj,
        })
        response = request.render("ess.ess_view_custody", values)
        return response

    @route(['/my/custody/in_progress'], type='http', auth='user', website=True)
    def view_custody_in_progress(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        custody_obj = request.env['custody.request'].sudo().search([('employee_id', '=', emb_obj.id)])

        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
            'custody_obj': custody_obj,
        })
        response = request.render("ess.ess_custody_in_progress", values)
        return response

    @route(['/add/custody_line'], type='http', auth='user', website=True)
    def add_custody_line(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        custody_description_obj = request.env['custody.description'].sudo().search([])

        print(">>>>>>>>>>>>>>>>>>id", post)
        # c_id = post['id']
        if post and request.httprequest.method == 'POST':
            print(">>>>>>>>>>>>>>>>>>id", post['params'])
            # print(">>>>>>>>>>>>>>>>>>c_id", c_id)
            print(">>>>>>>>>>>>>>>>>>custody_description_id", post['custody_description_id'])
            print(">>>>>>>>>>>>>>>>>>date", post['date'])
            print(">>>>>>>>>>>>>>>>>>amount", post['amount'])
            print(">>>>>>>>>>>>>>>>>>description", post['description'])
            post.update({
                'custody_id': post['id'],
                'custody_description_id': post['custody_description_id'],
                'date': post['date'],
                'amount': post['amount'],
                'description': post['description'],
            })
            request.env['custody.request.line'].sudo().create(post)
            custody_obj = request.env['custody.request'].sudo().search([('employee_id', '=', emb_obj.id)])

            values.update({
                'partner': request.env.user.partner_id,
                'employee': emb_obj,
                'custody_obj': custody_obj,
            })
            request.render("ess.ess_custody_in_progress", values)

        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
            'custody_description_obj': custody_description_obj,
        })
        response = request.render("ess.ess_add_custody_line", values)
        return response


    @route(['/request/passenger_mandate'], type='http', auth='user', website=True)
    def passenger_mandate(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])

        course_obj = request.env['training.course'].sudo().search([])
        course_place_obj = request.env['course.place'].sudo().search([])
        if post and request.httprequest.method == 'POST':
            if post['type'] == 'دوره':
                type = 'course'
            elif post['type'] == 'انتداب':
                type = 'mandate'
            elif post['type'] == 'ورشه عمل':
                type = 'work_shop'
            else:
                type = post['type']


            if post['course_type'] == 'داخلي':
                course_type = 'internal'
            elif post['course_type'] == 'خارجي':
                course_type = 'external'
            else:
                course_type = post['course_type']
            post.update({
                'employee_id': emb_obj.id,
                'employee_degree_id': emb_obj.employee_degree_id.id,
                'type': type,
                'course_type': course_type,
                'course_id': post['course_id'],
                'price': request.env['training.course'].sudo().browse(int(post['course_id'])).price,
                'start_date': request.env['training.course'].sudo().browse(int(post['course_id'])).start_date,
                'end_date': request.env['training.course'].sudo().browse(int(post['course_id'])).end_date,
                'number_of_days': request.env['training.course'].sudo().browse(int(post['course_id'])).number_of_days,
                'course_place_id': post['course_place_id'],
                'description': post['description'],
                'state': 'draft',
            })
            request.env['mandate.passenger'].sudo().create(post)
            # emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
            # courses_and_mandate_obj = request.env['mandate.passenger'].sudo().search([('employee_id', '=', emb_obj.id)])
            # # print("LLLLLLLLLLLL", courses_and_mandate_obj)
            # values.update({
            #     'partner': request.env.user.partner_id,
            #     'employee': emb_obj,
            #     'courses_and_mandate_obj': courses_and_mandate_obj,
            # })
            # response = request.render("ess.ess_view_courses_and_mandate", values)
            # return response
        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
            'course_obj': course_obj,
            'course_place_obj': course_place_obj,
        })

        response = request.render("ess.ess_passenger_mandate", values)
        return response

    @route(['/my/courses_and_mandate'], type='http', auth='user', website=True)
    def view_courses_and_mandate(self, redirect=None, **post):
        values = {}
        values = ESSPortal.check_modules(self)
        emb_obj = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        courses_and_mandate_obj = request.env['mandate.passenger'].sudo().search([('employee_id', '=', emb_obj.id)])

        values.update({
            'partner': request.env.user.partner_id,
            'employee': emb_obj,
            'courses_and_mandate_obj': courses_and_mandate_obj,
        })
        response = request.render("ess.ess_view_courses_and_mandate", values)
        return response