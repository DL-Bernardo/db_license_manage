# db_license_manager/models/license_notification.py
from odoo import models, api, _
from ..utils.license_verifier import verify_license, LicenseStatus
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class LicenseNotification(models.AbstractModel):
    _name = 'db.license.notification'
    _description = 'License Notification Logic'

    @api.model
    def _cron_check_license_expiration(self):
        """Daily cron for verifying license status and triggering automated email alerts."""
        token = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.token')
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')

        if not token:
            _logger.warning("License Cron: No license token configured.")
            return

        status, msg, exp_date, start_date = verify_license(token, db_uuid, env=self.env)

        if not exp_date and status not in [LicenseStatus.EXPIRED, LicenseStatus.INVALID]:
            return

        days_remaining = (exp_date.date() - datetime.now().date()).days if exp_date else -999

        # Notification milestones: 30, 15, 7, 5, 3, 2, 1, 0 days and when expired
        notify_days = [30, 15, 7, 5, 3, 2, 1, 0, -1, -3, -7]

        if days_remaining in notify_days or status in [LicenseStatus.EXPIRED, LicenseStatus.WARNING]:
            self.send_license_status_email(force_send=False)

    @api.model
    def send_license_status_email(self, recipients=None, force_send=True):
        """
        Sends formatted email regarding license status:
        - TO: Company alert email and System Administrators
        - CC: Support email (e.g. suporte@digitalub.ao)
        """
        ir_config = self.env['ir.config_parameter'].sudo()
        token = ir_config.get_param('db_license_manager.token')
        db_uuid = ir_config.get_param('database.uuid')

        status, msg, exp_date, start_date = verify_license(token, db_uuid, env=self.env)

        company = self.env.company
        company_name = company.name or "Company"
        company_vat = company.vat or "N/A"
        db_name = self.env.cr.dbname

        # 1. Target recipients (Company & Administrators)
        company_alert_email = ir_config.get_param('db_license_manager.company_notification_email') or company.email
        support_email = ir_config.get_param('db_license_manager.support_email') or 'suporte@digitalub.ao'

        admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
        admin_emails = []
        if admin_group:
            admin_emails = [u.email.strip() for u in admin_group.users if u.email and u.email.strip()]

        to_emails = set()
        if company_alert_email and company_alert_email.strip():
            for e in company_alert_email.split(','):
                if e.strip():
                    to_emails.add(e.strip())
        for e in admin_emails:
            to_emails.add(e)

        if recipients:
            if isinstance(recipients, str):
                for e in recipients.split(','):
                    if e.strip():
                        to_emails.add(e.strip())
            elif isinstance(recipients, (list, set)):
                for e in recipients:
                    if e and str(e).strip():
                        to_emails.add(str(e).strip())

        if not to_emails:
            if support_email:
                to_emails.add(support_email)
            else:
                _logger.warning("No recipients found for license status email.")
                return {'success': False, 'error': _('No recipient email address configured.')}

        # Days remaining
        days_remaining = (exp_date.date() - datetime.now().date()).days if exp_date else None

        # 2. Subject and Styles
        exp_date_str = exp_date.strftime('%d/%m/%Y') if exp_date else "Indefinite"
        start_date_str = start_date.strftime('%d/%m/%Y') if start_date else "N/A"

        if status == LicenseStatus.VALID:
            status_label = "ACTIVE &amp; VALID"
            status_color = "#28a745"
            status_bg = "#d4edda"
            subject = f"✅ [DIGITALUB] License Status - {company_name} (Active until {exp_date_str})"
            status_desc = f"Your system license is fully active and operational. Remaining validity: <b>{days_remaining} days</b>."
        elif status == LicenseStatus.WARNING:
            status_label = "EXPIRING SOON"
            status_color = "#856404"
            status_bg = "#fff3cd"
            subject = f"⚠️ [DIGITALUB - WARNING] License Expiring in {days_remaining} Days - {company_name}"
            status_desc = f"Attention: Your system license will expire in <b>{days_remaining} days</b> ({exp_date_str}). Please arrange renewal promptly to avoid service interruption."
        elif status == LicenseStatus.EXPIRED:
            status_label = "LICENSE EXPIRED"
            status_color = "#721c24"
            status_bg = "#f8d7da"
            subject = f"🚨 [DIGITALUB - CRITICAL] License Expired - {company_name}"
            status_desc = f"Your system license <b>expired on {exp_date_str}</b>. Access for regular users is currently restricted. Please contact technical support immediately to restore service."
        else:
            status_label = "INVALID / NOT FOUND"
            status_color = "#721c24"
            status_bg = "#f8d7da"
            subject = f"❌ [DIGITALUB - ALERT] Invalid License - {company_name}"
            status_desc = "A license discrepancy or missing license was detected for this database. Please contact technical support."

        # 3. HTML Body Construction
        email_to_str = ", ".join(sorted(list(to_emails)))
        cc_emails = [s.strip() for s in support_email.split(',') if s.strip() and s.strip() not in to_emails]
        email_cc_str = ", ".join(cc_emails) if cc_emails else False

        body_html = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; max-width: 650px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;">
            <div style="background-color: #002060; padding: 15px 20px; border-radius: 6px 6px 0 0; text-align: center; color: #ffffff;">
                <h2 style="margin: 0; font-size: 20px; font-weight: bold; letter-spacing: 0.5px;">DIGITALUB — Software License Management</h2>
            </div>
            
            <div style="padding: 20px 10px;">
                <p style="font-size: 14px; color: #334155; margin-top: 0;">
                    Dear <b>{company_name}</b> / Administration Team,
                </p>
                <p style="font-size: 13px; color: #475569; line-height: 1.6;">
                    This is an automated notice regarding the license status of your <b>Odoo ERP</b> instance.
                </p>

                <div style="margin: 20px 0; padding: 15px; border-radius: 6px; background-color: {status_bg}; border-left: 5px solid {status_color};">
                    <div style="font-size: 16px; font-weight: bold; color: {status_color}; margin-bottom: 5px;">
                        Status: {status_label}
                    </div>
                    <div style="font-size: 13px; color: #1e293b;">
                        {status_desc}
                    </div>
                </div>

                <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 0; color: #64748b; width: 40%;"><b>Company:</b></td>
                        <td style="padding: 8px 0; color: #0f172a;"><b>{company_name}</b> (VAT / NIF: {company_vat})</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 0; color: #64748b;"><b>Database:</b></td>
                        <td style="padding: 8px 0; color: #0f172a;">{db_name}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 0; color: #64748b;"><b>Issued On:</b></td>
                        <td style="padding: 8px 0; color: #0f172a;">{start_date_str}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 0; color: #64748b;"><b>Expiration Date:</b></td>
                        <td style="padding: 8px 0; color: #0f172a; font-weight: bold;">{exp_date_str}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 0; color: #64748b;"><b>Remaining Days:</b></td>
                        <td style="padding: 8px 0; color: #0f172a;">{days_remaining if days_remaining is not None else 'N/A'} days</td>
                    </tr>
                </table>

                <div style="margin-top: 25px; padding: 12px; background-color: #f8fafc; border-radius: 6px; font-size: 12px; color: #64748b; border: 1px dashed #cbd5e1;">
                    <b>Support &amp; Renewal Channels:</b><br/>
                    📧 Support Email: <a href="mailto:{support_email}" style="color: #002060; font-weight: bold;">{support_email}</a><br/>
                    🌐 Website: <a href="https://digitalub.ao" target="_blank" style="color: #002060;">https://digitalub.ao</a>
                </div>
            </div>

            <div style="border-top: 1px solid #e2e8f0; padding-top: 15px; text-align: center; font-size: 11px; color: #94a3b8;">
                Message automatically generated by DIGITALUB License Manager.<br/>
                &copy; Digitalub Angola — All rights reserved.
            </div>
        </div>
        """

        # 4. Sending email via configured mail server
        mail_server = self.env['ir.mail_server'].sudo().search([('active', '=', True)], limit=1)
        if mail_server and mail_server.smtp_user:
            sender_email = f"License Management <{mail_server.smtp_user}>"
        else:
            sender_email = company.email or support_email or 'suporte@digitalub.ao'

        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_to': email_to_str,
            'email_cc': email_cc_str or False,
            'email_from': sender_email,
            'reply_to': company.email or support_email or False,
            'mail_server_id': mail_server.id if mail_server else False,
            'auto_delete': False,
        }

        try:
            mail = self.env['mail.mail'].sudo().create(mail_values)
            if force_send:
                mail.send(auto_commit=True)
            _logger.info(f"License status email sent to: {email_to_str} (CC: {email_cc_str}) - State: {mail.state}")
            return {
                'success': True,
                'recipients': email_to_str,
                'cc': email_cc_str,
                'status': status,
                'subject': subject,
                'mail_id': mail.id,
                'mail_state': mail.state,
            }
        except Exception as e:
            _logger.error(f"Failed to send license status email: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }
