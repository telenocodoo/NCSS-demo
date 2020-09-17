# -*- coding: utf-8 -*-
{
    'name': "Hr Annual Leave Allocation",
    'summary': """
        Hr Annual Leave Allocation""",
    'description': """
        Hr Annual Leave Allocation
    """,
    'author': "Magdy, helcon",
    'website': "https://telenoc.org",
    'category': 'hr',
    'version': '0.1',
    'depends': ['hr', 'hr_contract', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/allocation_setting.xml',
        'views/hr_employee.xml',
        'views/end_of_service_award.xml',
    ],
}
