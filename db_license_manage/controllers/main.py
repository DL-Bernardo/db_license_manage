# db_license_manager/controllers/main.py
from odoo import http, api, SUPERUSER_ID
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from ..utils.license_verifier import verify_license, LicenseStatus
try:
    from markupsafe import Markup
except ImportError:
    from odoo.tools import Markup
import logging
import odoo

_logger = logging.getLogger(__name__)


class LicenseController(http.Controller):

    @http.route('/license/expired', type='http', auth="none")
    def license_expired(self, db=None, **kw):
        """
        Public endpoint for rendering the license expired / blocked notice.
        Uses auth="none" to ensure access even before session authentication.
        """
        db_name = db or request.params.get('db') or request.session.db
        if not db_name and odoo.tools.config.get('db_name'):
            db_name = odoo.tools.config['db_name']

        if not db_name:
            return self._get_fallback_html(
                "License Expired",
                "Your license has expired or is invalid. Please contact technical support."
            )

        try:
            registry = odoo.modules.registry.Registry(db_name)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})

                token = env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
                db_uuid = env['ir.config_parameter'].sudo().get_param('database.uuid')
                status, msg, exp_date, _ = verify_license(token, db_uuid, env=env)

                values = {
                    'message': msg,
                    'expiry_date': exp_date.strftime('%d/%m/%Y') if exp_date else False,
                    'status': status,
                }

                request.update_env(db_name)
                return request.render('db_license_manage.license_expired_page', values)

        except Exception as e:
            _logger.error(f"Error rendering license expired page for DB {db_name}: {str(e)}")
            return self._get_fallback_html(
                "Access Blocked",
                "Your license has expired. Please contact technical support to renew."
            )

    def _get_fallback_html(self, title, message):
        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{title}</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f8f9fa; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; color: #333; }}
                    .card {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); text-align: center; max-width: 460px; width: 90%; }}
                    h1 {{ color: #dc3545; margin-bottom: 16px; font-size: 26px; font-weight: 700; }}
                    p {{ line-height: 1.6; margin-bottom: 24px; color: #555; font-size: 16px; }}
                    .btn {{ background-color: #714B67; color: white; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block; transition: background 0.2s; }}
                    .btn:hover {{ background-color: #593b52; }}
                    .footer {{ margin-top: 28px; font-size: 12px; color: #999; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <div style="font-size: 56px; margin-bottom: 16px;">🚫</div>
                    <h1>{title}</h1>
                    <p>{message}</p>
                    <a href="/web/login" class="btn">Return to Login</a>
                    <div class="footer">Software protected by <strong>Digitalub Angola</strong></div>
                </div>
            </body>
        </html>
        """


class LicenseLogin(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        response = super(LicenseLogin, self).web_login(redirect=redirect, **kw)

        # Injects license status on GET so it renders immediately on the login screen
        if hasattr(response, 'qcontext') and response.qcontext is not None:
            response.qcontext.setdefault('license_status', False)
            response.qcontext.setdefault('license_expiry_date', False)
            try:
                env = request.env if hasattr(request, 'env') else None
                if env:
                    token = env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
                    db_uuid = env['ir.config_parameter'].sudo().get_param('database.uuid')
                    status, msg, exp_date, _ = verify_license(token, db_uuid, env=env)

                    response.qcontext.update({
                        'license_status': status,
                        'license_expiry_date': exp_date.strftime('%d/%m/%Y') if exp_date else False,
                    })

                    if status in [LicenseStatus.EXPIRED, LicenseStatus.INVALID]:
                        response.qcontext['license_login_status'] = {
                            'show': True,
                            'type': 'danger',
                            'icon': 'fa-ban',
                            'title': 'License Status' if status == LicenseStatus.INVALID else 'License Expired',
                            'message': msg,
                            'state': status,
                        }
                    elif status == LicenseStatus.WARNING:
                        response.qcontext['license_login_status'] = {
                            'show': True,
                            'type': 'warning',
                            'icon': 'fa-exclamation-triangle',
                            'title': 'License Warning',
                            'message': msg,
                            'state': status,
                        }
                    elif status == LicenseStatus.VALID:
                        response.qcontext['license_login_status'] = {
                            'show': True,
                            'type': 'success',
                            'icon': 'fa-shield',
                            'title': 'License Active',
                            'message': msg,
                            'state': status,
                        }
            except Exception as e:
                _logger.warning("Error fetching license status for login view: %s", e)

        # If not a POST login or no session authenticated, return standard view
        if not request.httprequest.method == 'POST' or not request.session.uid:
            return response

        # Post-authentication verification
        try:
            user = request.env['res.users'].sudo().browse(request.session.uid)

            # === ADMIN / SUPPORT BYPASS ===
            if user.id in [1, 2] or user.has_group('base.group_system'):
                return response

            # === REGULAR USER VERIFICATION ===
            token = request.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
            db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')

            status, msg, _, _ = verify_license(token, db_uuid, env=request.env)

            if status in [LicenseStatus.EXPIRED, LicenseStatus.INVALID]:
                _logger.info("License EXPIRED or INVALID - Redirecting regular user to expired page")
                db = request.session.db
                request.session.logout()
                if db:
                    request.session.db = db
                return request.redirect('/license/expired?db=%s' % (db or ''))

            elif status == LicenseStatus.WARNING:
                values = request.params.copy()
                msg_with_link = Markup(f"{msg} <br/><a href='/web' class='btn btn-sm btn-primary mt-2'>Continue to System</a>")
                values['warning'] = msg_with_link
                return request.render('web.login', values)

        except Exception as e:
            _logger.error(f"Error validating license post-login: {str(e)}")
            request.session.logout()
            values = request.params.copy()
            values['error'] = "Internal license validation error. Please contact technical support."
            return request.render('web.login', values)

        return response
