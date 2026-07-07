from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BangCongThang(models.Model):
    _name = 'bang_cong_thang'
    _description = 'Bảng công tháng'
    _rec_name = 'nhan_vien_id'
    _order = 'nam desc, thang desc'

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True
    )

    ma_dinh_danh = fields.Char(
        string='Mã định danh',
        related='nhan_vien_id.ma_dinh_danh',
        store=True,
        readonly=True
    )

    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban',
        related='nhan_vien_id.phong_ban_id',
        store=True,
        readonly=True
    )

    chuc_vu_id = fields.Many2one(
        'chuc_vu',
        string='Chức vụ',
        related='nhan_vien_id.chuc_vu_id',
        store=True,
        readonly=True
    )

    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string='Tháng', required=True)

    nam = fields.Integer(
        string='Năm',
        required=True,
        default=2026
    )

    tong_ngay_cong = fields.Float(
        string='Tổng ngày công',
        readonly=True
    )

    tong_gio_lam_them = fields.Float(
        string='Tổng giờ làm thêm',
        readonly=True
    )

    so_lan_di_muon = fields.Integer(
        string='Số lần đi muộn',
        readonly=True
    )

    so_ngay_vang = fields.Integer(
        string='Số ngày vắng',
        readonly=True
    )

    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_tong_hop', 'Đã tổng hợp'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
    ], string='Trạng thái', default='nhap')

    ghi_chu = fields.Text(string='Ghi chú')

    def action_tong_hop_cong(self):
        for record in self:
            if not record.nhan_vien_id or not record.thang or not record.nam:
                raise ValidationError('Vui lòng chọn nhân viên, tháng và năm.')

            thang_int = int(record.thang)
            nam_int = int(record.nam)

            cham_cong_records = self.env['cham_cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
            ])

            tong_ngay_cong = 0
            tong_gio_lam_them = 0
            so_lan_di_muon = 0
            so_ngay_vang = 0

            for cc in cham_cong_records:
                if not cc.ngay_cham_cong:
                    continue

                if cc.ngay_cham_cong.month == thang_int and cc.ngay_cham_cong.year == nam_int:
                    if cc.trang_thai in ['co_mat', 'di_muon']:
                        ngay_cong = cc.so_gio_lam / 8 if cc.so_gio_lam else 0
                        if ngay_cong > 1:
                            ngay_cong = 1
                        tong_ngay_cong += ngay_cong

                    if cc.trang_thai == 'di_muon':
                        so_lan_di_muon += 1

                    if cc.trang_thai == 'vang':
                        so_ngay_vang += 1

                    tong_gio_lam_them += cc.gio_lam_them

            record.tong_ngay_cong = tong_ngay_cong
            record.tong_gio_lam_them = tong_gio_lam_them
            record.so_lan_di_muon = so_lan_di_muon
            record.so_ngay_vang = so_ngay_vang
            record.trang_thai = 'da_tong_hop'

            record._tao_canh_bao_neu_bat_thuong()

    def _tao_canh_bao_neu_bat_thuong(self):
        for record in self:
            if record.so_lan_di_muon >= 3:
                self.env['canh_bao_cham_cong'].create({
                    'nhan_vien_id': record.nhan_vien_id.id,
                    'loai_canh_bao': 'di_muon_nhieu',
                    'noi_dung': 'Nhân viên đi muộn từ 3 lần trở lên trong tháng.',
                    'thang': record.thang,
                    'nam': record.nam,
                })

            if record.so_ngay_vang >= 2:
                self.env['canh_bao_cham_cong'].create({
                    'nhan_vien_id': record.nhan_vien_id.id,
                    'loai_canh_bao': 'vang_nhieu',
                    'noi_dung': 'Nhân viên vắng từ 2 ngày trở lên trong tháng.',
                    'thang': record.thang,
                    'nam': record.nam,
                })

            if record.tong_gio_lam_them >= 20:
                self.env['canh_bao_cham_cong'].create({
                    'nhan_vien_id': record.nhan_vien_id.id,
                    'loai_canh_bao': 'lam_them_nhieu',
                    'noi_dung': 'Nhân viên có tổng giờ làm thêm cao trong tháng.',
                    'thang': record.thang,
                    'nam': record.nam,
                })

    def action_duyet_bang_cong(self):
        for record in self:
            record.trang_thai = 'da_duyet'

    def action_tu_choi(self):
        for record in self:
            record.trang_thai = 'tu_choi'

    _sql_constraints = [
        (
            'unique_bang_cong_thang',
            'unique(nhan_vien_id, thang, nam)',
            'Mỗi nhân viên chỉ có một bảng công trong cùng tháng/năm!'
        )
    ]