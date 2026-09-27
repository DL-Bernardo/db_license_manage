import odoo
from odoo import http
from odoo.http import request
from ..utils.license_verifier import verify_license, LicenseStatus

# Odoo 19+ uses 'jsonrpc', Odoo 17 and 18 use 'json'
_route_type = 'jsonrpc' if getattr(odoo, 'release', None) and getattr(odoo.release, 'version_info', (0,))[0] >= 19 else 'json'


class LicenseSystrayController(http.Controller):

    @http.route('/db_license_manage/status', type=_route_type, auth='user')
    def get_license_status(self):
        token = request.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
        db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')

        status, msg, exp_date, _ = verify_license(token, db_uuid, env=request.env)

        days_remaining = 0
        expiration_date = None
        if exp_date:
            from datetime import datetime
            days_remaining = (exp_date.date() - datetime.now().date()).days
            expiration_date = exp_date.strftime('%d/%m/%Y')

        return {
            'status': status,
            'message': msg,
            'days_remaining': days_remaining,
            'expiration_date': expiration_date,
            'show_warning': status in [LicenseStatus.WARNING, LicenseStatus.EXPIRED, LicenseStatus.INVALID]
        }
