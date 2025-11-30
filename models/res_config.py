# db_license_manager/models/res_config.py
from odoo import models, fields, api, _
from ..utils.license_verifier import verify_license, LicenseStatus

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # O config_parameter guarda o valor na tabela ir_config_parameter automaticamente
    license_token = fields.Char(string="Chave de Licença", config_parameter='db_license_manager.token')
    public_key = fields.Text(string="Chave Pública RSA", groups="base.group_system")
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('db_license_manager.public_key', self.public_key)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['public_key'] = self.env['ir.config_parameter'].sudo().get_param('db_license_manager.public_key', default='')
        return res
    
    license_status_display = fields.Char(string="Estado da Licença", compute="_compute_license_status")
    license_expiration_date = fields.Date(string="Válido Até", compute="_compute_license_status")
    license_start_date = fields.Date(string="Data de Emissão", compute="_compute_license_status")

    @api.depends('license_token')
    def _compute_license_status(self):
        for record in self:
            token = record.license_token
            db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
            
            status, msg, exp_date, start_date = verify_license(token, db_uuid)
            
            record.license_status_display = f"[{status.upper()}] {msg}"
            record.license_expiration_date = exp_date.date() if exp_date else False
            record.license_start_date = start_date.date() if start_date else False
