# db_license_manager/models/license_notification.py
from odoo import models, api, _
from ..utils.license_verifier import verify_license
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class LicenseNotification(models.AbstractModel):
    _name = 'db.license.notification'
    _description = 'License Notification Logic'

    @api.model
    def _cron_check_license_expiration(self):
        token = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        
        if not token:
            return

        status, msg, exp_date, _ = verify_license(token, db_uuid)
        
        if not exp_date:
            return

        days_remaining = (exp_date - datetime.now()).days
        
        # Configurar dias para notificação: 15, 7, 5, 3, 1, 0, -1 (expirado)
        notify_days = [15, 7, 5, 3, 1, 0, -1]
        
        if days_remaining in notify_days:
            self._send_license_email(days_remaining, status, msg)

    @api.model
    def _send_license_email(self, days, status, msg):
        template = self.env.ref('db_license_manage.email_template_license_expiry', raise_if_not_found=False)
        if not template:
            _logger.warning("License email template not found.")
            return

        # Encontrar administradores (Grupo System)
        # Odoo 17: base.group_system é 'Settings', base.group_erp_manager é 'Administration'
        admin_group = self.env.ref('base.group_system')
        admins = admin_group.users
        
        for admin in admins:
            if not admin.email:
                continue
                
            ctx = {
                'days_remaining': days,
                'license_msg': msg,
                'license_status': status,
                'user_name': admin.name,
            }
            
            try:
                # Envia o e-mail usando o template
                template.with_context(ctx).send_mail(admin.id, force_send=True)
                _logger.info(f"License warning email sent to {admin.email} (Days: {days})")
            except Exception as e:
                _logger.error(f"Failed to send license email to {admin.email}: {str(e)}")
