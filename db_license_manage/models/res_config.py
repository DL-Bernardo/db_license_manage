# db_license_manager/models/res_config.py
from odoo import models, fields, api, _
from ..utils.license_verifier import verify_license, LicenseStatus


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    license_token = fields.Char(string="License Key / Token")
    public_key = fields.Text(string="RSA Public Key", groups="base.group_system")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.public_key', self.public_key)
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.token', self.license_token)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['public_key'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.public_key', default='')
        res['license_token'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.token', default='')
        return res

    license_status_display = fields.Char(string="Status Message", compute="_compute_license_status")
    license_state = fields.Selection([
        ('valid', 'Valid'),
        ('warning', 'Warning'),
        ('expired', 'Expired'),
        ('invalid', 'Invalid')
    ], string="License State", compute="_compute_license_status")
    license_expiration_date = fields.Date(string="Valid Until", compute="_compute_license_status")
    license_start_date = fields.Date(string="Issued On", compute="_compute_license_status")

    @api.depends('license_token')
    def _compute_license_status(self):
        for record in self:
            token = record.license_token
            db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')

            status, msg, exp_date, start_date = verify_license(token, db_uuid)

            record.license_state = status
            record.license_status_display = msg
            record.license_expiration_date = exp_date.date() if exp_date else False
            record.license_start_date = start_date.date() if start_date else False
