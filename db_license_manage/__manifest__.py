{
    'name': 'Database License Manager - DIGITALUB',
    'version': '17.0.1.0.1',
    'category': 'Tools',
    'summary': 'Software License Management with Automatic Blocking',
    'author': 'DIGITALUB ANGOLA',
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
    'price': 400,
    'currency': 'USD',
    'images': [
        'db_license_manage/static/description/banner.png',
        'db_license_manage/static/description/01.licenca_nao_encontrada.png',
        'db_license_manage/static/description/02.configurar_licenca.png',
        'db_license_manage/static/description/03.licenca_valida.png',
        'db_license_manage/static/description/04.Aviso_5_dias_licenca1.png',
        'db_license_manage/static/description/05.Aviso_5_dias_licenca.png',
        'db_license_manage/static/description/06.Licenca_expirada.png',
    ],
}
