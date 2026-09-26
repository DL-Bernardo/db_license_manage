# db_license_manager/models/res_config.py
from odoo import models, fields, api, _
from ..utils.license_verifier import verify_license, LicenseStatus


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    license_token = fields.Char(string="License Key / Token")
    public_key = fields.Text(string="RSA Public Key", groups="base.group_system")
    close_on_browser_exit = fields.Boolean(
        string="Close Session on Browser Exit",
        help="Force session termination when the user closes the browser."
    )
    license_support_email = fields.Char(
        string="Support Email (CC)",
        default="suporte@digitalub.ao"
    )
    license_company_notification_email = fields.Char(
        string="Company Email for License Alerts",
        help="Recipient email for automatic license warnings and expiration notices."
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.public_key', self.public_key or '')
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.token', self.license_token or '')
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.close_on_browser_exit', str(bool(self.close_on_browser_exit)))
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.support_email', self.license_support_email or '')
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.company_notification_email', self.license_company_notification_email or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['public_key'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.public_key', default='')
        res['license_token'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.token', default='')
        res['close_on_browser_exit'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.close_on_browser_exit', default='False') == 'True'
        res['license_support_email'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.support_email', default='suporte@digitalub.ao')
        res['license_company_notification_email'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.company_notification_email', default='')
        return res

    def action_send_license_status_email(self):
        """Immediately sends a formatted license status email to the company and support."""
        self.ensure_one()
        self.set_values()
        res = self.env['db.license.notification'].send_license_status_email(force_send=True)
        if res and res.get('success'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("License Email Sent"),
                    'message': _("License status email sent successfully to %s (CC: %s).") % (
                        res.get('recipients'), res.get('cc') or _('None')
                    ),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            err = res.get('error') if res else _("Unknown error")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Failed to Send Email"),
                    'message': _("Could not send license email: %s") % err,
                    'type': 'danger',
                    'sticky': True,
                }
            }

    license_status_display = fields.Char(string="Status Message", compute="_compute_license_status")
    license_state = fields.Selection([
        ('valid', 'Valid'),
        ('warning', 'Warning'),
        ('expired', 'Expired'),
        ('invalid', 'Invalid')
    ], string="License State", compute="_compute_license_status")
    license_expiration_date = fields.Date(string="Valid Until", compute="_compute_license_status")
    license_start_date = fields.Date(string="Issued On", compute="_compute_license_status")

    @api.depends('license_token', 'public_key')
    def _compute_license_status(self):
        for record in self:
            token = record.license_token
            db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')

            status, msg, exp_date, start_date = verify_license(
                token, db_uuid, env=self.env, public_key_override=record.public_key
            )

            record.license_state = status
            record.license_status_display = msg
            record.license_expiration_date = exp_date.date() if exp_date else False
            record.license_start_date = start_date.date() if start_date else False


# Monkeypatch odoo.http.get_session_max_inactivity to support expiration upon closing browser
import odoo.http
if hasattr(odoo.http, 'get_session_max_inactivity'):
    original_get_session_max_inactivity = odoo.http.get_session_max_inactivity

    def custom_get_session_max_inactivity(env):
        if env:
            try:
                close_on_browser_exit = env['ir.config_parameter'].sudo().get_param('db_license_manager.close_on_browser_exit')
                if close_on_browser_exit == 'True':
                    return None  # None sets cookie without max-age (expires on browser exit)
            except Exception:
                pass
        return original_get_session_max_inactivity(env)

    odoo.http.get_session_max_inactivity = custom_get_session_max_inactivity
