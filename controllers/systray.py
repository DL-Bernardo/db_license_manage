# db_license_manager/controllers/systray.py
from odoo import http
from odoo.http import request
from ..utils.license_verifier import verify_license, LicenseStatus

class LicenseSystrayController(http.Controller):

    @http.route('/db_license_manage/status', type='json', auth='user')
    def get_license_status(self):
        token = request.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
        db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')
        
        status, msg, exp_date, _ = verify_license(token, db_uuid)
        
        # Calculate days remaining for display
        days_remaining = 0
        if exp_date:
            from datetime import datetime
            days_remaining = (exp_date - datetime.now()).days

        return {
            'status': status,
            'message': msg,
            'days_remaining': days_remaining,
            'show_warning': status in [LicenseStatus.WARNING, LicenseStatus.EXPIRED, LicenseStatus.INVALID]
        }
