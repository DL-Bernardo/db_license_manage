# db_license_manager/__manifest__.py
{
    'name': 'Database License Manager - DIGITALUB',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Gestão de Licença de Software com Bloqueio Automático',
    'author': 'Digitalub',
    'depends': ['base', 'web'],
    'external_dependencies': {
        'python': ['pyjwt', 'cryptography'],
    },
    'data': [
        'views/res_config_settings_views.xml',
        'views/login_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': ['static/description/banner.png'],
}