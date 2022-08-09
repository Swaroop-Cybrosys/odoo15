{
    'name': 'Vehicle Rental',
    'version': '15.0.5.0',
    'sequence': -1,
    'author': 'leo',
    'summary': 'Vehicle Rental Service version 15.0.5.0',
    'category': 'Sales',
    'description': """
    This is the Vehicle Rental service module version 15.0.5.0. 
    You can rent vehicles from wide variety of of collection we have in an easy
     and convenient way.
     """,

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/fleet_view.xml',
        'views/vehicle_rental_views.xml',
        'views/vehicle_rental_request.xml',
        'wizard/report_vehicle_rental.xml',
        'data/ir_sequence_data.xml',
        'data/auto_time_check.xml',

        'report/vehicle_rental_report.xml',
        'report/vehicle_rental_report_template.xml',

    ],
    'depends': ['base','fleet','account','web','mail'],
    'installable': True,
    'application': True,
    'auto_install': False,

    'assets': {
        'web.assets_backend': [
            'vehicle_rental/static/src/js/action_manager_report.esm.js',
        ],

    },
    'license': 'LGPL-3',

}
