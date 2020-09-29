# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CustodyRequest(models.Model):
    _name = 'custody.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    expense_account_move_id = fields.Many2one('account.move', 'Journal Expense')
    liquidated_account_move_id = fields.Many2one('account.move', 'Journal Liquidated')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    description = fields.Text()
    reason = fields.Text()
    amount = fields.Float()
    remaining_amount = fields.Float(compute='get_remaining_amount')
    date = fields.Date()
    exchange_item_ids = fields.One2many('custody.request.line', 'custody_id')
    move_line_ids = fields.One2many('account.move.line', 'custody_id',
                                    domain=lambda self: [('move_id', '=', self.expense_account_move_id.id)])
    liquidated_move_line_ids = fields.One2many('account.move.line', 'custody_id',
                                               domain=lambda self: [('move_id', '=', self.liquidated_account_move_id.id)])
    is_direct_manager = fields.Boolean(compute='get_direct_manager')
    is_liquidated = fields.Boolean(compute='get_is_liquidated')
    state = fields.Selection([('draft', 'Draft'),
                              ('direct_manager_approve', 'Direct Manager Approve'),
                              ('department_manager_approve', 'Department Manager Approve'),
                              ('center_manager_approve', 'Center Manager Approve'),
                              ('accounting_approve', 'Accounting Approve'),
                              ('paid', 'Paid'),
                              ('in_progress', 'In Progress'),
                              ('liquidated', 'Liquidated'),
                              ('refuse', 'Refuse'),
                              ('done', 'Done'),
                              ], default='draft', tracking=True,)

    def get_direct_manager(self):
        current_user_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).id
        for record in self:
            if record.employee_id and record.employee_id.parent_id:
                if record.employee_id.parent_id.id == current_user_id:
                    record.is_direct_manager = True
                else:
                    record.is_direct_manager = False
            else:
                record.is_direct_manager = False

    def get_is_liquidated(self):
        for record in self:
            if record.remaining_amount == 0.0:
                record.is_liquidated = True
            else:
                record.is_liquidated = False

    @api.depends('amount', 'exchange_item_ids')
    def get_remaining_amount(self):
        for record in self:
            total_amount = sum([line.amount for line in self.exchange_item_ids])
            record.remaining_amount = record.amount-total_amount

    @api.constrains('amount', 'exchange_item_ids', 'remaining_amount')
    def _constrains_remaining_amount(self):
        total_amount = sum([line.amount for line in self.exchange_item_ids])
        if self.amount < total_amount:
            raise UserError(_("Remaining Amount Must Be Less Than Or Equal To Amount"))

    def action_refuse(self):
        for record in self:
            if not record.reason:
                raise UserError(_("Please Add the reason of Refuse"))
            else:
                self.state = 'refuse'

    def action_direct_manager_approve(self):
        self.state = 'direct_manager_approve'

    def action_department_manager_approve(self):
        self.state = 'department_manager_approve'

    def center_manager_approve(self):
        self.state = 'center_manager_approve'

    def accounting_approve(self):
        self.state = 'accounting_approve'

    def create_account_move(self, journal, label, debit_account_id, credit_account_id, amount, address_home_id):
        account_move_obj = self.env['account.move']
        account_move_id = account_move_obj.create({
            'journal_id': journal,
            'ref': label,
        })
        journal_line = self.with_context(dict(self._context, check_move_validity=False)).env['account.move.line']
        journal_line.create({
            'move_id': account_move_id.id,
            'account_id': debit_account_id,
            'name': label,
            'debit': amount,
            'credit': 0.0,
            'partner_id': address_home_id,
            'custody_id': self.id,
        })
        journal_line.create({
            'move_id': account_move_id.id,
            'account_id': credit_account_id,
            'name': label,
            'debit': 0.0,
            'credit': amount,
            'partner_id': address_home_id,
            'custody_id': self.id,
        })
        return account_move_id

    def paid_action(self):
        journal = self.env.user.company_id.custody_journal_id.id
        label = self.env.user.company_id.label
        debit_account_id = self.env.user.company_id.debit_account_id.id
        credit_account_id = self.env.user.company_id.credit_account_id.id
        amount = self.amount
        address_home_id = self.employee_id.address_home_id.id
        account_move_obj = self.create_account_move(journal, label, debit_account_id, credit_account_id, amount, address_home_id)
        self.expense_account_move_id = account_move_obj.id
        self.state = 'paid'

    def in_progress_action(self):
        self.state = 'in_progress'

    def make_liquidated_action(self):
        self.state = 'liquidated'

    def liquidated_action(self):
        journal = self.env.user.company_id.custody_journal_id.id
        label = self.env.user.company_id.label
        credit_account_id = self.env.user.company_id.debit_account_id.id
        debit_account_id = self.env.user.company_id.expense_account_id.id
        amount = self.amount
        address_home_id = self.employee_id.address_home_id.id
        account_move_obj = self.create_account_move(journal, label, debit_account_id, credit_account_id, amount, address_home_id)
        self.liquidated_account_move_id = account_move_obj.id
        self.state = 'done'

    def set_to_draft(self):
        self.state = 'draft'


class CustodyRequestLine(models.Model):
    _name = 'custody.request.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    amount = fields.Float()
    date = fields.Date()
    description = fields.Text()
    attach_invoice = fields.Binary()
    custody_id = fields.Many2one('custody.request')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    custody_id = fields.Many2one('custody.request')
