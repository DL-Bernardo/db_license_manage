# db_license_manager/utils/license_verifier.py
import jwt
import logging
from datetime import datetime
from odoo import _

_logger = logging.getLogger(__name__)


class LicenseStatus:
    VALID = 'valid'
    WARNING = 'warning'
    EXPIRED = 'expired'
    INVALID = 'invalid'


def get_public_key():
    """
    Retrieves RSA public key from system parameters.
    """
    from odoo.http import request
    if request:
        return request.env['ir.config_parameter'].sudo().get_param('db_license_manager.public_key')
    return None


def format_public_key(key_str):
    """
    Formats the public key into proper PEM format with headers and newlines.
    """
    if not key_str:
        return None

    key_str = key_str.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "")
    key_str = "".join(key_str.split())

    formatted_key = "-----BEGIN PUBLIC KEY-----\n"
    for i in range(0, len(key_str), 64):
        formatted_key += key_str[i:i+64] + "\n"
    formatted_key += "-----END PUBLIC KEY-----"
    return formatted_key


def verify_license(token, current_db_uuid):
    """
    Validates JWT token against RSA Public Key and database UUID.
    Returns: (status, message, expiration_date, start_date)
    """
    if not token:
        return LicenseStatus.INVALID, _("License not found. Please contact support."), None, None

    public_key = get_public_key()
    if not public_key:
        return LicenseStatus.INVALID, _("RSA Public Key is not configured."), None, None

    public_key = format_public_key(public_key)

    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"], leeway=60, options={"verify_iat": False})

        if payload.get('uuid') != current_db_uuid:
            return LicenseStatus.INVALID, _("License is invalid for this database UUID."), None, None

        exp_timestamp = payload.get('exp')
        exp_date = datetime.fromtimestamp(exp_timestamp)

        iat_timestamp = payload.get('iat', 0)
        start_date = datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None

        days_remaining = (exp_date - datetime.now()).days

        if 0 <= days_remaining <= 5:
            msg = _("Warning: Your license will expire in %s days.") % days_remaining
            return LicenseStatus.WARNING, msg, exp_date, start_date

        return LicenseStatus.VALID, _("License Active & Valid"), exp_date, start_date

    except jwt.ExpiredSignatureError:
        return LicenseStatus.EXPIRED, _("Your license has expired. Please contact support."), None, None
    except jwt.InvalidTokenError as e:
        _logger.error(f"License Error: {e}")
        return LicenseStatus.INVALID, _("License token is corrupt or invalid."), None, None
    except Exception as e:
        _logger.error(f"Generic License Error: {e}")
        return LicenseStatus.INVALID, _("License validation error. Please contact support."), None, None
