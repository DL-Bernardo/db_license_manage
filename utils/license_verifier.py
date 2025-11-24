# db_license_manager/utils/license_verifier.py
import jwt
import logging
from datetime import datetime
from odoo import _

_logger = logging.getLogger(__name__)

# --- SUBSTITUA ISTO PELA SUA CHAVE PÚBLICA RSA REAL ---
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz... (Coloca a tua chave aqui)
-----END PUBLIC KEY-----"""

class LicenseStatus:
    VALID = 'valid'
    WARNING = 'warning'
    EXPIRED = 'expired'
    INVALID = 'invalid'

def verify_license(token, current_db_uuid):
    """
    Valida o token JWT e o UUID da base de dados.
    Retorna: (status, mensagem, data_expiracao)
    """
    if not token:
        return LicenseStatus.INVALID, _("Licença não encontrada."), None

    try:
        # Decodifica usando a Chave Pública
        # O pyjwt valida automaticamente a assinatura e a data 'exp' (expiração)
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        
        # Verifica se a licença pertence a esta base de dados (Anti-Cópia)
        if payload.get('uuid') != current_db_uuid:
            return LicenseStatus.INVALID, _("Licença inválida para este UUID de base de dados."), None

        # Cálculo para avisos (Grace Period)
        exp_timestamp = payload.get('exp')
        exp_date = datetime.fromtimestamp(exp_timestamp)
        days_remaining = (exp_date - datetime.now()).days

        if 0 <= days_remaining <= 15:
            msg = _("Aviso: A sua licença expira em %s dias.") % days_remaining
            return LicenseStatus.WARNING, msg, exp_date

        return LicenseStatus.VALID, _("Licença Ativa"), exp_date

    except jwt.ExpiredSignatureError:
        return LicenseStatus.EXPIRED, _("Sua licença expirou. Contacte o suporte."), None
    except jwt.InvalidTokenError as e:
        _logger.error(f"License Error: {e}")
        return LicenseStatus.INVALID, _("Licença corrompida ou inválida."), None
    except Exception as e:
        _logger.error(f"Generic License Error: {e}")
        return LicenseStatus.INVALID, _("Erro na validação da licença."), None