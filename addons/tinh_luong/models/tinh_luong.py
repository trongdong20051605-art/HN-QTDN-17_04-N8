from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar


class TinhLuong(models.Model):
    _name = 'tinh_luong'
    _description = 'Bảng tính lương nhân viên'
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
        ('1', 'Tháng 1'),
        ('2', 'Tháng 2'),
        ('3', 'Tháng 3'),
        ('4', 'Tháng 4'),
        ('5', 'Tháng 5'),
        ('6', 'Tháng 6'),
        ('7', 'Tháng 7'),
        ('8', 'Tháng 8'),
        ('9', 'Tháng 9'),
        ('10', 'Tháng 10'),
        ('11', 'Tháng 11'),
        ('12', 'Tháng 12'),
    ], string='Tháng', required=True)

    nam = fields.Integer(
        string='Năm',
        required=True,
        default=2026
    )

    hop_dong_id = fields.Many2one(
    'hop_dong_lao_dong',
    string='Hợp đồng lao động'
    )

    luong_co_ban = fields.Float(
        string='Lương cơ bản',
        compute='_compute_du_lieu_luong',
        store=True,
        readonly=True
    )

    phu_cap = fields.Float(
        string='Phụ cấp tháng',
        compute='_compute_du_lieu_luong',
        store=True,
        readonly=True
    )

    ty_le_bao_hiem = fields.Float(
        string='Tỷ lệ bảo hiểm (%)',
        compute='_compute_du_lieu_luong',
        store=True,
        readonly=True
    )

    tong_ngay_cong = fields.Float(
        string='Tổng ngày công',
        compute='_compute_du_lieu_cham_cong',
        store=True
    )

    tong_gio_lam_them = fields.Float(
        string='Tổng giờ làm thêm',
        compute='_compute_du_lieu_cham_cong',
        store=True
    )

    tien_lam_them = fields.Float(
        string='Tiền làm thêm',
        compute='_compute_luong',
        store=True
    )

    tien_bao_hiem = fields.Float(
        string='Tiền bảo hiểm',
        compute='_compute_luong',
        store=True
    )

    thuong = fields.Float(
        string='Thưởng',
        default=0
    )

    khau_tru = fields.Float(
        string='Khấu trừ',
        default=0
    )

    thuc_linh = fields.Float(
        string='Thực lĩnh',
        compute='_compute_luong',
        store=True
    )

    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ phê duyệt'),
        ('da_duyet', 'Đã phê duyệt'),
        ('tu_choi', 'Từ chối'),
        ('da_tra', 'Đã trả lương'),
    ], string='Trạng thái', default='nhap')

    nguoi_phe_duyet_id = fields.Many2one(
        'res.users',
        string='Người phê duyệt',
        readonly=True
    )

    ngay_phe_duyet = fields.Datetime(
        string='Ngày phê duyệt',
        readonly=True
    )

    ly_do_tu_choi = fields.Text(
        string='Lý do từ chối'
    )

    ghi_chu_luong = fields.Text(
        string='Ghi chú lương'
    )

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_du_lieu_cham_cong(self):
        for record in self:
            record.tong_ngay_cong = 0
            record.tong_gio_lam_them = 0

            if not record.nhan_vien_id or not record.thang or not record.nam:
                continue

                bang_cong = self.env['bang_cong_thang'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('thang', '=', record.thang),
                    ('nam', '=', record.nam),
                    ('trang_thai', '=', 'da_duyet'),
                ], limit=1)

                if bang_cong:
                    record.tong_ngay_cong = bang_cong.tong_ngay_cong
                    record.tong_gio_lam_them = bang_cong.tong_gio_lam_them
                    continue

            thang_int = int(record.thang)
            nam_int = int(record.nam)

            cham_cong_records = self.env['cham_cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
            ])

            tong_ngay_cong = 0
            tong_gio_lam_them = 0

            for cc in cham_cong_records:
                if not cc.ngay_cham_cong:
                    continue

                if cc.ngay_cham_cong.month == thang_int and cc.ngay_cham_cong.year == nam_int:
                    if cc.trang_thai in ['co_mat', 'di_muon']:
                        ngay_cong = cc.so_gio_lam / 8 if cc.so_gio_lam else 0

                        if ngay_cong > 1:
                            ngay_cong = 1

                        tong_ngay_cong += ngay_cong

                    tong_gio_lam_them += cc.gio_lam_them

            record.tong_ngay_cong = tong_ngay_cong
            record.tong_gio_lam_them = tong_gio_lam_them

    @api.depends(
        'luong_co_ban',
        'phu_cap',
        'ty_le_bao_hiem',
        'tong_ngay_cong',
        'tong_gio_lam_them',
        'thuong',
        'khau_tru',
        'thang',
        'nam'
    )
    def _compute_luong(self):
        for record in self:
            if not record.thang or not record.nam:
                record.tien_lam_them = 0
                record.tien_bao_hiem = 0
                record.thuc_linh = 0
                continue

            thang_int = int(record.thang)
            nam_int = int(record.nam)

            so_ngay_trong_thang = calendar.monthrange(nam_int, thang_int)[1]

            luong_ngay = record.luong_co_ban / 26 if record.luong_co_ban else 0
            luong_theo_cong = luong_ngay * record.tong_ngay_cong

            phu_cap_ngay = record.phu_cap / so_ngay_trong_thang if record.phu_cap else 0
            phu_cap_theo_cong = phu_cap_ngay * record.tong_ngay_cong

            record.tien_lam_them = record.tong_gio_lam_them * 50000

            record.tien_bao_hiem = record.luong_co_ban * record.ty_le_bao_hiem / 100

            record.thuc_linh = (
                luong_theo_cong
                + phu_cap_theo_cong
                + record.thuong
                + record.tien_lam_them
                - record.tien_bao_hiem
                - record.khau_tru
            )

    def action_gui_phe_duyet(self):
        for record in self:
            record.trang_thai = 'cho_duyet'

    def action_phe_duyet(self):
        for record in self:
            record.trang_thai = 'da_duyet'
            record.nguoi_phe_duyet_id = self.env.user.id
            record.ngay_phe_duyet = fields.Datetime.now()

    def action_tu_choi(self):
        for record in self:
            record.trang_thai = 'tu_choi'

    def action_da_tra_luong(self):
        for record in self:
            record.trang_thai = 'da_tra'

    def action_dat_ve_nhap(self):
        for record in self:
            record.trang_thai = 'nhap'

    @api.depends(
        'nhan_vien_id',
        'hop_dong_id',
        'hop_dong_id.muc_luong',
        'hop_dong_id.phu_cap',
        'hop_dong_id.ty_le_bao_hiem'
    )
    def _compute_du_lieu_luong(self):
        for record in self:
            if record.hop_dong_id:
                record.luong_co_ban = record.hop_dong_id.muc_luong or 0
                record.phu_cap = record.hop_dong_id.phu_cap or 0
                record.ty_le_bao_hiem = record.hop_dong_id.ty_le_bao_hiem or 0

            elif record.nhan_vien_id:
                record.luong_co_ban = record.nhan_vien_id.luong_co_ban or 0
                record.phu_cap = record.nhan_vien_id.phu_cap or 0
                record.ty_le_bao_hiem = record.nhan_vien_id.ty_le_bao_hiem or 0

            else:
                record.luong_co_ban = 0
                record.phu_cap = 0
                record.ty_le_bao_hiem = 0

    @api.constrains('thuong', 'khau_tru')
    def _check_so_tien(self):
        for record in self:
            if record.thuong < 0:
                raise ValidationError('Thưởng không được nhỏ hơn 0.')
            if record.khau_tru < 0:
                raise ValidationError('Khấu trừ không được nhỏ hơn 0.')
    @api.onchange('nhan_vien_id')
    def _onchange_nhan_vien_id(self):
        for record in self:
            if record.nhan_vien_id:
                hop_dong = self.env['hop_dong_lao_dong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('trang_thai', '=', 'hieu_luc')
                ], order='ngay_bat_dau desc, id desc', limit=1)

                if not hop_dong:
                    hop_dong = self.env['hop_dong_lao_dong'].search([
                        ('nhan_vien_id', '=', record.nhan_vien_id.id)
                    ], order='ngay_bat_dau desc, id desc', limit=1)

                record.hop_dong_id = hop_dong.id if hop_dong else False
            else:
                record.hop_dong_id = False
