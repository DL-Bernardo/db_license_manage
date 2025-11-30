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
            elif status == LicenseStatus.WARNING:
                # Aviso de licença próxima ao vencimento
                # Não bloqueia o login, mas precisamos renderizar a página novamente para mostrar o aviso
                # Se retornarmos 'response' direto, o Odoo redireciona para /web e o usuário não vê o aviso no login
                
                # Opção A: Redirecionar para backend e mostrar notificação lá (complexo)
                # Opção B: Manter na tela de login com aviso e botão "Continuar" (mais seguro)
                # Opção C: Injetar aviso na sessão e deixar o usuário entrar (o que tentamos, mas o redirect limpa ou ignora)

                # Vamos tentar forçar a renderização da página de login com o aviso, 
                # mas permitindo que o usuário clique em "Entrar" novamente ou tenha um link para prosseguir.
                # Porem, como o usuário JÁ está logado (session.uid existe), se renderizarmos o login, 
                # ele pode ficar confuso.
                
                # Melhor abordagem para UX: Deixar entrar e usar o Notification do Odoo (Bus).
                # Mas como o requisito é na tela de login, o problema é que o 'response' original é um REDIRECT (303).
                
                # Se quisermos mostrar na tela de login, temos que INTERROMPER o redirect.
                values = request.params.copy()
                # Adicionamos um link para o usuário prosseguir, já que ele está logado
                msg_with_link = f"{msg} <br/><a href='/web' class='btn btn-sm btn-primary mt-2'>Continuar para o Sistema</a>"
                values['warning'] = msg_with_link
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