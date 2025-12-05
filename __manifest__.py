# db_license_manager/__manifest__.py
{
    'name': 'Database License Manager - DIGITALUB',
    'version': '17.0.1.0.1',
    'category': 'Tools',
    'summary': 'Software License Management with Automatic Blocking',
    'author': 'Digitalub',
    'depends': ['base', 'web', 'website', 'auth_signup', 'mail'],
    'external_dependencies': {
        'python': ['pyjwt', 'cryptography'],
    },
    'data': [
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/res_config_settings_views.xml',
        'views/login_templates.xml',
        'views/login_warning.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'db_license_manage/static/src/css/login.css',
        ],
        'web.assets_backend': [
            'db_license_manage/static/src/js/systray_license.js',
            'db_license_manage/static/src/xml/systray_license.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 385,
    'currency': 'USD',
    'images': ['static/description/banner.png']
}