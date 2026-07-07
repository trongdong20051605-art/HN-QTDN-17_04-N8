from odoo import models, fields
from odoo.exceptions import ValidationError


class BangCongThangAutoLuong(models.Model):
    _inherit = 'bang_cong_thang'

    phieu_luong_id = fields.Many2one(
        'tinh_luong',
        string='Phiếu lương tự tạo',
        readonly=True
    )

    def action_duyet_bang_cong(self):
        result = super(BangCongThangAutoLuong, self).action_duyet_bang_cong()

        for record in self:
            record._tu_dong_tao_phieu_luong()

        return result

    def _tu_dong_tao_phieu_luong(self):
        for record in self:
            if not record.nhan_vien_id:
                raise ValidationError('Bảng công chưa có nhân viên.')

            if not record.thang or not record.nam:
                raise ValidationError('Bảng công chưa có tháng/năm.')

            hop_dong = self.env['hop_dong_lao_dong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('trang_thai', '=', 'hieu_luc')
            ], order='ngay_bat_dau desc, id desc', limit=1)

            if not hop_dong:
                hop_dong = self.env['hop_dong_lao_dong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id)
                ], order='ngay_bat_dau desc, id desc', limit=1)

            phieu_luong = self.env['tinh_luong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('thang', '=', record.thang),
                ('nam', '=', record.nam),
            ], limit=1)

            vals = {
                'nhan_vien_id': record.nhan_vien_id.id,
                'thang': record.thang,
                'nam': record.nam,
                'trang_thai': 'nhap',
                'ghi_chu_luong': (
                    'Phiếu lương được tự động tạo sau khi duyệt bảng công tháng.'
                ),
            }

            if 'hop_dong_id' in self.env['tinh_luong']._fields and hop_dong:
                vals['hop_dong_id'] = hop_dong.id

            if phieu_luong:
                phieu_luong.write(vals)
            else:
                phieu_luong = self.env['tinh_luong'].create(vals)

            if hasattr(phieu_luong, '_compute_du_lieu_cham_cong'):
                phieu_luong._compute_du_lieu_cham_cong()

            if hasattr(phieu_luong, '_compute_luong'):
                phieu_luong._compute_luong()

            record.phieu_luong_id = phieu_luong.id