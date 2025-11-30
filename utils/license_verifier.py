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
    Recupera a chave pública dos parâmetros do sistema.
    """
    from odoo.http import request
    # Tenta pegar do request.env se disponível (contexto web)
    if request:
        return request.env['ir.config_parameter'].sudo().get_param('db_license_manager.public_key')
    # Fallback para script/shell (pode precisar de ajuste dependendo do contexto de chamada)
    return None

def format_public_key(key_str):
    """
    Tenta formatar a chave pública para o formato PEM correto.
    """
    if not key_str:
        return None
        
    # Remove headers existing if any to normalize
    key_str = key_str.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "")
    # Remove all whitespace
    key_str = "".join(key_str.split())
    
    formatted_key = "-----BEGIN PUBLIC KEY-----\n"
    # Chunk by 64 chars
    for i in range(0, len(key_str), 64):
        formatted_key += key_str[i:i+64] + "\n"
    formatted_key += "-----END PUBLIC KEY-----"
    return formatted_key

def verify_license(token, current_db_uuid):
    """
    Valida o token JWT e o UUID da base de dados.
    Retorna: (status, mensagem, data_expiracao, data_inicio)
    """
    if not token:
        return LicenseStatus.INVALID, _("Licença não encontrada."), None, None

    public_key = get_public_key()
    if not public_key:
        return LicenseStatus.INVALID, _("Chave Pública não configurada no sistema."), None, None

    # Formata a chave para garantir que está válida (headers, newlines)
    public_key = format_public_key(public_key)

    try:
        # Decodifica usando a Chave Pública
        # O pyjwt valida automaticamente a assinatura e a data 'exp' (expiração)
        # Adicionamos leeway=60 para tolerar pequenas diferenças de relógio (1 min)
        payload = jwt.decode(token, public_key, algorithms=["RS256"], leeway=60, options={"verify_iat": False})
        
        # Verifica se a licença pertence a esta base de dados (Anti-Cópia)
        if payload.get('uuid') != current_db_uuid:
            return LicenseStatus.INVALID, _("Licença inválida para este UUID de base de dados."), None, None

        # Cálculo para avisos (Grace Period)
        exp_timestamp = payload.get('exp')
        exp_date = datetime.fromtimestamp(exp_timestamp)
        
        # Data de início (Issued At)
        iat_timestamp = payload.get('iat', 0)
        start_date = datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None

        days_remaining = (exp_date - datetime.now()).days

        if 0 <= days_remaining <= 5:
            msg = _("Aviso: A sua licença expira em %s dias.") % days_remaining
            return LicenseStatus.WARNING, msg, exp_date, start_date

        return LicenseStatus.VALID, _("Licença Ativa"), exp_date, start_date

    except jwt.ExpiredSignatureError:
        return LicenseStatus.EXPIRED, _("Sua licença expirou. Contacte o suporte."), None, None
    except jwt.InvalidTokenError as e:
        _logger.error(f"License Error: {e}")
        return LicenseStatus.INVALID, _("Licença corrompida ou inválida."), None, None
    except Exception as e:
        _logger.error(f"Generic License Error: {e}")
        return LicenseStatus.INVALID, _("Erro na validação da licença."), None, None