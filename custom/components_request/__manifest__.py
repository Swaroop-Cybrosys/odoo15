{
    'name': "Components Request",
    'version': '15.0.1.0',
    'sequence': -5,
    'author': 'leo',
    'summary': """
        Summary of components request module""",
    'category': 'Uncategorized',
    'description': """
        descriptio of components request module
    """,
    'depends': ['base', 'product', 'hr', 'stock', 'purchase'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/components_request_view.xml',
        'data/ir_sequence_data.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
