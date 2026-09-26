# db_license_manager/controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from ..utils.license_verifier import verify_license, LicenseStatus
try:
    from markupsafe import Markup
except ImportError:
    from odoo.tools import Markup
import logging

_logger = logging.getLogger(__name__)
_logger.info("Loading LicenseLogin Controller...")


class LicenseLogin(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        # Execute default Odoo login first
        response = super(LicenseLogin, self).web_login(redirect=redirect, **kw)

        # Check license status on GET (pre-login view) so status appears immediately on screen
        if request.httprequest.method != 'POST' and hasattr(response, 'qcontext') and response.qcontext is not None:
            try:
                token = request.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
                db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')
                status, msg, exp_date, _ = verify_license(token, db_uuid)

                if status in [LicenseStatus.EXPIRED, LicenseStatus.INVALID]:
                    response.qcontext['license_login_status'] = {
                        'show': True,
                        'type': 'danger',
                        'icon': 'fa-ban',
                        'title': 'License Status' if status == LicenseStatus.INVALID else 'License Expired',
                        'message': msg,
                    }
                elif status == LicenseStatus.WARNING:
                    response.qcontext['license_login_status'] = {
                        'show': True,
                        'type': 'warning',
                        'icon': 'fa-exclamation-triangle',
                        'title': 'License Warning',
                        'message': msg,
                    }
            except Exception as e:
                _logger.warning("Error checking license on login GET: %s", e)

        # If login was not POST or session uid is not set, return standard response
        if not request.httprequest.method == 'POST' or not request.session.uid:
            return response

        # If user authenticated successfully, verify license permissions
        try:
            user = request.env['res.users'].sudo().browse(request.session.uid)

            # === ADMIN / SUPPORT BYPASS ===
            # Allow OdooBot (1), Admin (2), or users with system configuration access
            if user.id in [1, 2] or user.has_group('base.group_system'):
                return response

            # === VERIFICATION FOR REGULAR USERS ===
            token = request.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
            db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')

            status, msg, _, _ = verify_license(token, db_uuid)
            _logger.info(f"License Check - Status: {status}, Msg: {msg}")

            if status in [LicenseStatus.EXPIRED, LicenseStatus.INVALID]:
                _logger.info("License EXPIRED or INVALID - Blocking login for regular user")
                request.session.logout()
                values = request.params.copy()
                values['error'] = msg
                return request.render('web.login', values)
            elif status == LicenseStatus.WARNING:
                _logger.info("License WARNING - Showing warning on login page")
                values = request.params.copy()
                msg_with_link = Markup(f"{msg} <br/><a href='/web' class='btn btn-sm btn-primary mt-2'>Continue to System</a>")
                values['warning'] = msg_with_link
                return request.render('web.login', values)

        except Exception as e:
            _logger.error(f"Error validating license: {str(e)}")
            request.session.logout()
            values = request.params.copy()
            values['error'] = "Internal license validation error. Please contact support."
            return request.render('web.login', values)

        return response
