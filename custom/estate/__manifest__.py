{
    'name': 'Real Estate',
    'version': '2.0',
    'sequence': 0,
    'author': 'leo',
    'summary': 'This is the summary',
    'category': 'test module',
    'description': "this is the description 2.0",
    'website': 'https://www.odoo.com/real_esate',
    'data': [
        # 'security/groups.xml',
        'views/estate_property_views.xml',
        'security/ir.model.access.csv'
    ],
    'depends': [
        'base_setup',
        'mail'

    ],
    'installable': True,
    'application': True,
    'auto_install': False

}
