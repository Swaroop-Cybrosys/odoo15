{
    'name': "monthly_discount_limit",
    'version': '15.0.1.0',
    'sequence': -7,
    'author': 'leo',
    'summary': 'monthly_discount_limit version 15.0.1.0',
    'category': 'Sales',
    'description': """
    This is the Monthly Discount Limit module version 15.0.1.0.
     """,
    'depends': ['base', 'sale'],
    'data': [
        'views/views.xml',
        'data/monthly_discount_reset.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
