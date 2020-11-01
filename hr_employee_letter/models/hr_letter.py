# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LetterLetter(models.Model):
    _name = 'letter.letter'
    _inherit = ['mail.thread', 'mail.template', 'mail.activity.mixin']

    name = fields.Char()
    template_id = fields.Html('Template')


class LetterRequest(models.Model):
    _name = 'letter.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    Date = fields.Date()
    letter_type_id = fields.Many2one('letter.letter')
    request_id = fields.Many2one('hr.employee', 'Requester')
    employee_id = fields.Many2one('hr.employee', 'Approval')
    note = fields.Text()
    state = fields.Selection(selection=[('Draft', 'Draft'),
                                        ('Approve', 'Approve'),
                                        ('Cancel', 'Cancel'),
                                        ], default='Draft')

    def action_draft(self):
        for record in self:
            record.state = 'Draft'

    def action_approve(self):
        for record in self:
            record.state = 'Approve'

    def action_cancel(self):
        for record in self:
            record.state = 'Cancel'
