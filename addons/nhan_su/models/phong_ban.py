from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Quản lý phòng ban'
    _rec_name = 'ten_phong_ban'

    ma_phong_ban = fields.Char(string='Mã phòng ban', required=True)
    ten_phong_ban = fields.Char(string='Tên phòng ban', required=True)
    mo_ta = fields.Text(string='Mô tả')
    truong_phong_id = fields.Many2one('nhan_vien', string='Trưởng phòng')
    ngay_thanh_lap = fields.Date(string='Ngày thành lập')
    trang_thai = fields.Selection([
        ('hoat_dong', 'Hoạt động'),
        ('tam_dung', 'Tạm dừng'),
    ], string='Trạng thái', default='hoat_dong')

    so_nhan_vien = fields.Integer(
        string='Số nhân viên',
        compute='_compute_so_nhan_vien',
        store=False
    )
    nhan_vien_ids = fields.One2many(
        'nhan_vien',
        'phong_ban_id',
        string='Danh sách nhân viên'
    )
    @api.depends('nhan_vien_ids')
    def _compute_so_nhan_vien(self):
        for record in self:
            record.so_nhan_vien = len(record.nhan_vien_ids)
        _sql_constraints = [
        ('unique_ma_phong_ban', 'unique(ma_phong_ban)', 'Mã phòng ban không được trùng!')
    ]
