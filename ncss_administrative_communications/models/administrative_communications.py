# -*- coding: utf-8 -*-
from . import calverter
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AdministrativeCommunicationCategory(models.Model):
    _name = 'administrative.communication.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "code"

    name = fields.Char()
    code = fields.Char()


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
    name = fields.Char()
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


class AdministrativeCommunication(models.Model):
    _name = 'administrative.communication'
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char()
    treatment_type = fields.Selection([('in', 'Incoming'), ('out', 'Outgoing'), ('internal', 'Internal')])
    administrative_communication_in_id = fields.Many2one('administrative.communication', 'Incoming')
    administrative_communication_out_id = fields.Many2one('administrative.communication', 'Outgoing')
    Category = fields.Many2one('administrative.communication.category')
    category_name = fields.Char()
    transactions_number = fields.Char()
    years = fields.Many2one('administrative.communication.years')
    reference_number = fields.Char()
    transaction_date = fields.Date('Date')
    hijri_date = fields.Char('Date', compute='_calculate_hijri_date', store=True)
    source_id = fields.Many2one('administrative.communication.source')
    destination_id = fields.Many2one('administrative.communication.source')
    transfer_to_id = fields.Many2one('administrative.communication.management')
    contact_id = fields.Many2one('administrative.communication.contact')
    transfer_date = fields.Date('Date')
    transfer_number = fields.Char()
    attachments = fields.Integer()
    subject = fields.Char()
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
                              ('done', 'Done'),
                              ], default='draft')

    @api.model
    def create(self, values):
        if values['treatment_type'] == 'in':
            values['sequence'] = self.env['ir.sequence'].next_by_code('administrative.communication.import')
        elif values['treatment_type'] == 'out':
            values['sequence'] = self.env['ir.sequence'].next_by_code('administrative.communication.export')
        else:
            values['sequence'] = self.env['ir.sequence'].next_by_code('administrative.communication.internal')
        return super(AdministrativeCommunication, self).create(values)

    @api.onchange('Category')
    def onchange_category(self):
        self.category_name = self.Category.name

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
            'domain': [('transfer_to_id', 'in', self.env.user.transfer_to_ids.ids)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'target': 'current',
        }

    def assign_to_department_action(self):
        if not self.transfer_to_id:
            raise UserError(_('Please Add The Department.'))
        self.state = 'reviewed'

    def assign_to_employee_action(self):
        if not self.contact_id:
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
        default['destination_id'] = self.source_id.id
        default['transfer_to_id'] = False
        default['source_id'] = self.env.ref('ncss_administrative_communications.demo_contact_ncss').id
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

    def action_done(self):
        self.state = 'done'

    def set_to_draft(self):
        self.state = 'draft'


class AdministrativeCommunicationLine(models.Model):
    _name = 'administrative.communication.line'

    administrative_communication_id = fields.Many2one('administrative.communication')
    attached_by_id = fields.Many2one('administrative.communication.contact')
    recipient_by_id = fields.Many2one('administrative.communication.contact')
    source_id = fields.Many2one('administrative.communication.source')
    transfer_to_id = fields.Many2one('administrative.communication.management')
    sender_type = fields.Many2one('administrative.communication.sender')
    date_and_time = fields.Datetime('Date And Time')
    notes = fields.Char()

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
