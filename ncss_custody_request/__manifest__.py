# -*- coding: utf-8 -*-
{
    'name': 'ncss_custody_request',
    'version': '13.0.1',
    'summary': 'ncss_custody_request',
    'category': 'ncsscustody_request',
    'author': 'Magdy,TeleNoc',
    'description': """
    custody_request
    """,
    'depends': ['base', 'mail', 'hr', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/custody_request.xml',
        'views/custody_request_setting.xml',
    ]
}
