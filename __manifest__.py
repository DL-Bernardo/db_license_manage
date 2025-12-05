# db_license_manager/__manifest__.py
{
    'name': 'Database License Manager - DIGITALUB',
    'version': '17.0.1.0.1',
    'category': 'Tools',
    'summary': 'Gestão de Licença de Software com Bloqueio Automático',
    'author': 'Digitalub',
<<<<<<< HEAD
    'depends': ['base', 'web', 'auth_signup', 'mail'],
=======
    'depends': ['base', 'web', 'website', 'auth_signup', 'mail'],
>>>>>>> e3d7358826008ff0f97c0789d2aac03e9fadd3f4
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
<<<<<<< HEAD
    'price': 385,
    'currency': 'USD',
=======
>>>>>>> e3d7358826008ff0f97c0789d2aac03e9fadd3f4
    'images': ['static/description/banner.png']
}