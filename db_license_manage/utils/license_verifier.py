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


def get_public_key(env=None):
    """Retrieves RSA Public Key from system parameters."""
    if env:
        return env['ir.config_parameter'].sudo().get_param('db_license_manager.public_key')
    from odoo.http import request
    if request and hasattr(request, 'env'):
        return request.env['ir.config_parameter'].sudo().get_param('db_license_manager.public_key')
    return None


def format_public_key(key_str):
    """Formats RSA Public Key into standardized PEM format."""
    if not key_str:
        return None

    # Remove headers existing if any to normalize
    key_str = key_str.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "")
    # Remove all whitespace
    key_str = "".join(key_str.split())

    formatted_key = "-----BEGIN PUBLIC KEY-----\n"
    for i in range(0, len(key_str), 64):
        formatted_key += key_str[i:i+64] + "\n"
    formatted_key += "-----END PUBLIC KEY-----"
    return formatted_key


def verify_license(token, current_db_uuid, env=None, public_key_override=None):
    """
    Validates JWT token against database UUID.
    Returns: (status, message, expiration_date, start_date)
    """
    if not token:
        return LicenseStatus.INVALID, _("License not found. Please contact support."), None, None

    token = "".join(str(token).split())

    public_key = public_key_override or get_public_key(env)
    if not public_key:
        return LicenseStatus.INVALID, _("RSA Public Key is not configured."), None, None

    public_key = format_public_key(public_key)

    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"], leeway=60, options={"verify_iat": False})

        # Anti-Copy: Database UUID validation
        if payload.get('uuid') != current_db_uuid:
            return LicenseStatus.INVALID, _("License is invalid for this database UUID."), None, None

        exp_timestamp = payload.get('exp')
        exp_date = datetime.fromtimestamp(exp_timestamp)

        iat_timestamp = payload.get('iat', 0)
        start_date = datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None

        days_remaining = (exp_date.date() - datetime.now().date()).days

        if 0 <= days_remaining <= 5:
            msg = _("Warning: Your license will expire in %s days.") % days_remaining
            return LicenseStatus.WARNING, msg, exp_date, start_date

        return LicenseStatus.VALID, _("License Active & Valid"), exp_date, start_date

    except jwt.ExpiredSignatureError:
        exp_date = None
        start_date = None
        try:
            unverified_payload = jwt.decode(
                token, public_key, algorithms=["RS256"],
                options={"verify_signature": True, "verify_exp": False, "verify_iat": False}
            )
            exp_timestamp = unverified_payload.get('exp')
            exp_date = datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
            iat_timestamp = unverified_payload.get('iat', 0)
            start_date = datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None
        except Exception:
            pass
        return LicenseStatus.EXPIRED, _("Your license has expired. Please contact support."), exp_date, start_date
    except jwt.InvalidTokenError as e:
        _logger.error(f"License Error: {e}")
        return LicenseStatus.INVALID, _("License token is corrupt or invalid."), None, None
    except Exception as e:
        _logger.error(f"Generic License Error: {e}")
        return LicenseStatus.INVALID, _("License validation error. Please contact support."), None, None
