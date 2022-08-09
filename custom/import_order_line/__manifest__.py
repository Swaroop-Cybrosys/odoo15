{
    'name': "import_order_line",
    'version': '15.0.5.0',
    'sequence':-6,
    'author': "L",
    'category': 'Uncategorized',
    'depends': ['base','sale'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/import_order_line.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
