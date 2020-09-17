# -*- coding: utf-8 -*-
from . import calverter
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from datetime import timedelta


class AdministrativeCommunicationCategory(models.Model):
    _name = 'administrative.communication.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char()
    parent_id = fields.Many2one('administrative.communication.category')


class AdministrativeCommunicationYears(models.Model):
    _name = 'administrative.communication.years'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()


class AdministrativeCommunicationSource(models.Model):
    _name = 'administrative.communication.source'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    contact_line_ids = fields.One2many('administrative.communication.contact.line', 'source_id')


class AdministrativeCommunicationManagement(models.Model):
    _name = 'administrative.communication.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char('Department')
    user_id = fields.Many2one('res.users', 'Department Manager')
    contact_line_ids = fields.One2many('administrative.communication.contact.line', 'transfer_to_id')


class AdministrativeCommunicationSender(models.Model):
    _name = 'administrative.communication.sender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()


class AdministrativeCommunicationContactLine(models.Model):
    _name = 'administrative.communication.contact.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    contact_id = fields.Many2one('administrative.communication.contact')
    source_id = fields.Many2one('administrative.communication.source')
    transfer_to_id = fields.Many2one('administrative.communication.management')


class AdministrativeCommunicationContact(models.Model):
    _name = 'administrative.communication.contact'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()


class AdministrativeCommunicationProcedures(models.Model):
    _name = 'administrative.communication.procedures'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    no_of_days = fields.Integer()


class AdministrativeCommunication(models.Model):
    _name = 'administrative.communication'
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char()
    treatment_type = fields.Selection([('in', 'Incoming'), ('out', 'Outgoing'), ('internal', 'Internal')])
    administrative_communication_in_id = fields.Many2one('administrative.communication', 'Incoming')
    administrative_communication_out_id = fields.Many2one('administrative.communication', 'Outgoing')
    # change to selection
    post_type = fields.Selection([('paper', 'Paper'), ('fax', 'Fax'), ('electronic', 'Electronic')])
    category_name = fields.Char()
    #post type

    assign_to_id = fields.Many2one('administrative.communication.category', 'Assign To')
    assign_to_department_id = fields.Many2one('administrative.communication.category', 'Assign To Department')


    # new field
    nature_of_transaction = fields.Selection([('personal', 'Personal'), ('public', 'Public'), ('secret', 'Secret')])
    way_of_send = fields.Selection([('manual', 'manual'), ('email', 'email'), ('fax', 'Fax'), ('post', 'post')])
    #
    transactions_number = fields.Char()
    years = fields.Many2one('administrative.communication.years')
    reference_number = fields.Char()
    transaction_date = fields.Date('Transaction Date', default=fields.Date.today())
    hijri_date = fields.Char('Date', compute='_calculate_hijri_date', store=True)
    # source_id = fields.Many2one('administrative.communication.source')
    source_id = fields.Many2one('administrative.communication.category')
    destination_id = fields.Many2one('administrative.communication.source')
    transfer_to_id = fields.Many2one('administrative.communication.management')
    user_id = fields.Many2one('res.users')
    contact_id = fields.Many2one('administrative.communication.contact')
    transfer_date = fields.Date('Receipt Date', default=fields.Date.today())
    allow_transfer_date = fields.Boolean()
    edit_transaction_date = fields.Boolean()
    transfer_number = fields.Char()
    attachments = fields.Integer()
    subject = fields.Text()
    file_number = fields.Char()
    notes = fields.Char()
    sender_type = fields.Many2one('administrative.communication.sender')
    transaction_line_ids = fields.One2many('administrative.communication.line', 'administrative_communication_id',
                                           copy=True)
    transaction_attachment_line_ids = fields.One2many('administrative.communication.attachments',
                                                      'administrative_communication_id', copy=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('reviewed', 'sent to department'),
                              ('assigned', 'Sent To Employee'),
                              ('outgoing', 'Outgoing Sent'),
                              ('barcode', 'Barcode'),
                              ('instrument', 'Instrument'),
                              ('done', 'Done'),
                              ], default='draft')
    state_in = fields.Selection(related='state')
    state_out = fields.Selection(related='state')

    @api.model
    def create(self, values):
        if values['treatment_type'] == 'in':
            values['sequence'] = self.env['ir.sequence'].next_by_code('administrative.communication.import')
        elif values['treatment_type'] == 'out':
            values['sequence'] = self.env['ir.sequence'].next_by_code('administrative.communication.export')
        else:
            values['sequence'] = self.env['ir.sequence'].next_by_code('administrative.communication.internal')
        return super(AdministrativeCommunication, self).create(values)

    @api.onchange('transfer_to_id')
    def onchange_transfer_to_id(self):
        self.user_id = self.transfer_to_id.user_id.id

    @api.onchange('assign_to_id')
    def onchange_assign_to_id(self):
        self.assign_to_department_id = self.assign_to_id.id

    @api.depends('transaction_date')
    def _calculate_hijri_date(self):
        cal = calverter.Calverter()
        for rec in self:
            if rec.transaction_date:
                d = rec.transaction_date
                jd = cal.gregorian_to_jd(d.year, d.month, d.day)
                hj = cal.jd_to_islamic(jd)
                rec.hijri_date = str(hj[2]) + "/" + str(hj[1]) + "/" + str(hj[0])

    def action_administrative_communication(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assigned To My Department',
            'res_model': 'administrative.communication',
            'domain': [('user_id', '=', self.env.user.id)],
            'view_type': 'form',
            'view_mode': 'tree,form',
        }

    def assign_to_department_action(self):
        if not self.transfer_to_id:
            raise UserError(_('Please Add The Department.'))
        self.state = 'reviewed'

    def assign_to_employee_action(self):
        if not self.user_id:
            raise UserError(_('Please Add The Specialized Employee.'))
        self.state = 'assigned'

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        return super(AdministrativeCommunication, self).copy(default)

    def outgoing_treatment_action(self):
        self.state = 'outgoing'
        default={}
        default['treatment_type'] = 'out'
        # default['destination_id'] = self.source_id.id
        default['transfer_to_id'] = False
        # default['source_id'] = self.env.ref('ncss_administrative_communications.demo_contact_ncss').id
        default['source_id'] = self.env.ref('ncss_administrative_communications.demo_source_direction').id
        default['assign_to_id'] = self.source_id.id
        y = self.copy(default)
        y.administrative_communication_in_id = self.id
        self.administrative_communication_out_id = y.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Administrative Communication',
            'res_model': 'administrative.communication',
            'res_id': y.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }

    def action_assign_to(self):
        ncss_department_id = self.env.user.ncss_department_id
        return {
            'type': 'ir.actions.act_window',
            'name': 'administrative communication wizard',
            'res_model': 'administrative.communication.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {
                'default_ncss_department_id': ncss_department_id.id if ncss_department_id else False,
                'default_position': self.env.user.position,
                        },
            'target': 'new',
        }

    def outgoing_barcode_action(self):
        self.state = 'barcode'
        return self.env.ref('ncss_administrative_communications.barcode_report').report_action(self)

    def outgoing_instrument_action(self):
        self.state = 'instrument'
        return self.env.ref('ncss_administrative_communications.report_administrative_communication').report_action(self)

    def action_done(self):
        self.state = 'done'

    def set_to_draft(self):
        self.state = 'draft'


class AdministrativeCommunicationWizard(models.TransientModel):
    _name = 'administrative.communication.wizard'

    user_id = fields.Many2one('res.users')
    procedure_id = fields.Many2one('administrative.communication.procedures')
    sender_notes = fields.Char()
    # receipt_notes = fields.Char()
    ncss_department_id = fields.Many2one('administrative.communication.management')
    position = fields.Selection([('regular', 'Regular'),
                                 ('center_manager', 'Center Manager'),
                                 ('department_manager', 'Manager'),
                                 ])
    no_of_days = fields.Integer()
    due_date = fields.Date(default=fields.date.today())

    @api.onchange('procedure_id')
    def onchange_procedure_id(self):
        self.no_of_days = self.procedure_id.no_of_days

    @api.onchange('no_of_days')
    def onchange_no_of_days(self):
        self.due_date = fields.date.today() + timedelta(days=self.no_of_days)

    @api.onchange('position', 'ncss_department_id')
    def onchange_position(self):
        users = []
        user_obj = self.env['res.users']
        if self.position == 'regular':
            user_ids = user_obj.search([('position', '=', 'regular'),
                                        ('ncss_department_id', '=', self.ncss_department_id.id)])
            for user in user_ids:
                users.append(user.id)

        elif self.position == 'center_manager':
            user_ids = user_obj.search([('position', '=', 'department_manager')])
            for user in user_ids:
                users.append(user.id)

        elif self.position == 'department_manager':
            user_ids = user_obj.search([])
            for user in user_ids:
                users.append(user.id)
        else:
            users = []
        domain = {'user_id': [('id', 'in', users)]}
        return {'domain': domain}

    def action_assign_to(self):
        print(self.env.context.get('active_ids')[0])
        communication_id = self.env['administrative.communication'].browse(self.env.context.get('active_ids')[0])
        communication_lines = self.env['administrative.communication.line']
        communication_lines.create({
            'administrative_communication_id': self.env.context.get('active_ids')[0],
            'user_attached_id': self.env.user.id,
            'user_id': self.user_id.id,
            'procedure_id': self.procedure_id.id,
            'due_date': self.due_date,
            'sender_notes': self.sender_notes,
        })
        if communication_id.state == 'reviewed':
            communication_id.state = 'assigned'


class AdministrativeCommunicationLine(models.Model):
    _name = 'administrative.communication.line'
    _rec_name = "administrative_communication_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    administrative_communication_id = fields.Many2one('administrative.communication')
    attached_by_id = fields.Many2one('administrative.communication.contact')
    recipient_by_id = fields.Many2one('administrative.communication.contact')
    user_attached_id = fields.Many2one('res.users')
    user_id = fields.Many2one('res.users')
    source_id = fields.Many2one('administrative.communication.source')
    transfer_to_id = fields.Many2one('administrative.communication.management')
    procedure_id = fields.Many2one('administrative.communication.procedures')
    sender_type = fields.Many2one('administrative.communication.sender')
    date_and_time = fields.Datetime('Date And Time', default=datetime.datetime.now())
    notes = fields.Char()
    sender_notes = fields.Char()
    receipt_notes = fields.Char()
    due_date = fields.Date()
    subject = fields.Text(related="administrative_communication_id.subject")

    @api.onchange('source_id', 'transfer_to_id')
    def onchange_source_id(self):
        contacts = []
        transfers = []
        for record in self:
            for c in record.source_id.contact_line_ids:
                contacts.append(c.contact_id.id)
            for t in record.transfer_to_id.contact_line_ids:
                transfers.append(t.contact_id.id)
        domain = {'attached_by_id': [('id', 'in', contacts)],'recipient_by_id': [('id', 'in', transfers)]}
        return {'domain': domain}


class AdministrativeCommunicationAttachments(models.Model):
    _name = 'administrative.communication.attachments'

    administrative_communication_id = fields.Many2one('administrative.communication')
    attachments = fields.Binary()
    description = fields.Char()
