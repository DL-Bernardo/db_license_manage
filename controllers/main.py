# db_license_manager/controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from ..utils.license_verifier import verify_license, LicenseStatus

class LicenseLogin(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        # Executa o login padrão do Odoo primeiro
        response = super(LicenseLogin, self).web_login(redirect=redirect, **kw)
        
        # Se o login falhou (senha errada) ou não é POST, retorna o padrão
        if not request.httprequest.method == 'POST' or not request.session.uid:
            return response
            
        # Se o utilizador logou com sucesso, vamos verificar a licença
        try:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            
            # === BYPASS PARA ADMIN/SUPORTE ===
            # Permite OdooBot (1), Admin (2) ou utilizadores com acesso total às definições
            if user.id in [1, 2] or user.has_group('base.group_system'):
                return response

            # === VERIFICAÇÃO ===
            token = request.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
            db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')
            
            status, msg, _, _ = verify_license(token, db_uuid)
            
            if status in [LicenseStatus.EXPIRED, LicenseStatus.INVALID]:
                # Bloqueio: Faz logout forçado
                request.session.logout()
                
                # Prepara a mensagem de erro para exibir na tela
                values = request.params.copy()
                values['error'] = msg
                return request.render('web.login', values)
            
            # Se for WARNING, podes adicionar lógica aqui para injetar aviso, mas o login prossegue
            
        except Exception as e:
            # Em caso de erro crítico no código, garantir que admin consegue entrar, mas outros não
            # Log do erro para debug
            request.env['ir.logging'].sudo().create({
                'name': 'License Manager',
                'type': 'server',
                'level': 'error',
                'dbname': request.session.db,
                'message': f"Erro na verificação de licença: {str(e)}",
                'path': 'main.py',
                'func': 'web_login',
                'line': '0',
            })
            
            request.session.logout()
            values = request.params.copy()
            values['error'] = "Erro interno de validação de licença. Contacte o suporte."
            return request.render('web.login', values)

        return response