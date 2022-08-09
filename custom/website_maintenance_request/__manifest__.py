{
    'name': 'Website Maintenance Request',
    'version': '15.0.1.0',
    'sequence': -15,
    'author': 'leo',
    'summary': 'Website Maintenance Request version 15.0.1.0',
    'category': 'Website',
    'description': """
    This is the Website Maintenance Request module version 15.0.1.0.
     """,

    'data': [
        'views/website_maintance_request_views.xml',
        'data/mail_template.xml',
        'views/template.xml',

    ],
    'depends': ['base','website','mail','hr_maintenance'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
