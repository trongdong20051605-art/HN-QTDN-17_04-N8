from odoo import models, fields


class CanhBaoChamCong(models.Model):
    _name = 'canh_bao_cham_cong'
    _description = 'Cảnh báo chấm công bất thường'
    _order = 'create_date desc'

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True
    )

    loai_canh_bao = fields.Selection([
        ('di_muon_nhieu', 'Đi muộn nhiều lần'),
        ('vang_nhieu', 'Vắng nhiều lần'),
        ('lam_them_nhieu', 'Làm thêm nhiều'),
    ], string='Loại cảnh báo')

    noi_dung = fields.Text(string='Nội dung cảnh báo')

    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string='Tháng')

    nam = fields.Integer(string='Năm', default=2026)

    da_xu_ly = fields.Boolean(
        string='Đã xử lý',
        default=False
    )