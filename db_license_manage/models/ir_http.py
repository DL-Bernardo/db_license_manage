# db_license_manager/models/ir_http.py
from odoo import models
from odoo.http import request
from ..utils.license_verifier import verify_license, LicenseStatus
import logging
from werkzeug.exceptions import HTTPException

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _authenticate(cls, *args, **kwargs):
        res = super(IrHttp, cls)._authenticate(*args, **kwargs)

        # If no active session or user, proceed normally
        if not request.session.uid:
            return res

        # Prevent redirect loops on public / authentication endpoints
        if request.httprequest.path in ['/license/expired', '/web/login', '/web/database/selector']:
            return res

        try:
            # Superuser and admin bypass (OdooBot: 1, Admin: 2, or group_system)
            if request.session.uid in [1, 2]:
                return res

            user = request.env['res.users'].sudo().browse(request.session.uid)
            if not user.exists() or user.has_group('base.group_system'):
                return res

            # Verify active license in real time
            token = request.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
            db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')

            status, msg, _, _ = verify_license(token, db_uuid, env=request.env)

            if status in [LicenseStatus.EXPIRED, LicenseStatus.INVALID]:
                _logger.warning(f"Active session blocked due to license status: {status}. User ID: {request.session.uid}")
                db = request.session.db
                request.session.logout()
                if db:
                    request.session.db = db

                # Do not raise HTTP 302 on JSON-RPC calls, as it corrupts webclient RPC responses
                if request.httprequest.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.httprequest.mimetype == 'application/json':
                    return res

                raise HTTPException(response=request.redirect('/license/expired?db=%s' % (db or '')))
        except HTTPException:
            raise
        except Exception as e:
            _logger.error(f"License check in _authenticate failed safely: {e}")
            return res

        return res
