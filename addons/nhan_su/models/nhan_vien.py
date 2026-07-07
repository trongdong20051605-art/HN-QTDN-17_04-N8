from odoo import models, fields, api
from odoo.exceptions import ValidationError
import unicodedata

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Quản lý nhân viên'
    _rec_name = 'ho_ten'
    _order = 'id desc'

    # =========================
    # THÔNG TIN CÁ NHÂN
    # =========================
    ma_dinh_danh = fields.Char(
        string='Mã định danh',
        copy=False
    )

    ho_dem = fields.Char(
        string='Họ tên đệm'
    )

    ten = fields.Char(
        string='Tên',
        required=True
    )

    ho_ten = fields.Char(
        string='Họ và tên',
        compute='_compute_ho_ten',
        store=True
    )

    ngay_sinh = fields.Date(
        string='Ngày sinh'
    )

    tuoi = fields.Integer(
        string='Tuổi',
        compute='_compute_tuoi',
        store=True
    )

    que_quan = fields.Char(
        string='Quê quán'
    )

    anh = fields.Binary(
        string='Ảnh nhân viên'
    )

    gioi_tinh = fields.Selection([
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('khac', 'Khác'),
    ], string='Giới tính')

    so_dien_thoai = fields.Char(
        string='Số điện thoại'
    )

    email = fields.Char(
        string='Email'
    )

    dia_chi = fields.Text(
        string='Địa chỉ'
    )

    can_cuoc_cong_dan = fields.Char(
        string='Căn cước công dân'
    )

    ngay_cap_cccd = fields.Date(
        string='Ngày cấp CCCD'
    )

    noi_cap_cccd = fields.Char(
        string='Nơi cấp CCCD'
    )

    so_nguoi_bang_tuoi = fields.Integer(
        string='Số người bằng tuổi',
        compute='_compute_so_nguoi_bang_tuoi',
        store=False
    )
    def name_get(self):
        result = []
        for record in self:
            ho_dem = record.ho_dem or ''
            ten = record.ten or ''
            ma = record.ma_dinh_danh or ''

            ho_ten = (ho_dem + ' ' + ten).strip()

            if ma:
                name = f'{ho_ten} [{ma}]'
            else:
                name = ho_ten

            result.append((record.id, name))

        return result
    def _bo_dau_tieng_viet(self, text):
        if not text:
            return ''

        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        text = text.replace('đ', 'd').replace('Đ', 'D')
        text = text.lower()
        text = ''.join(char for char in text if char.isalnum() or char.isspace())
        text = ' '.join(text.split())

        return text

    def _tao_ma_dinh_danh(self, ho_dem, ten):
        ho_dem_khong_dau = self._bo_dau_tieng_viet(ho_dem or '')
        ten_khong_dau = self._bo_dau_tieng_viet(ten or '')

        cac_tu_ho_dem = ho_dem_khong_dau.split()
        chu_cai_dau = ''.join(tu[0] for tu in cac_tu_ho_dem if tu)

        return ten_khong_dau + chu_cai_dau

    @api.onchange('ho_dem', 'ten')
    def _onchange_tao_ma_dinh_danh(self):
        for record in self:
            if record.ho_dem or record.ten:
                record.ma_dinh_danh = record._tao_ma_dinh_danh(record.ho_dem, record.ten)
    @api.model
    def create(self, vals):
        if not vals.get('ma_dinh_danh'):
            ho_dem = vals.get('ho_dem', '')
            ten = vals.get('ten', '')
            vals['ma_dinh_danh'] = self._tao_ma_dinh_danh(ho_dem, ten)

        return super(NhanVien, self).create(vals)

    def write(self, vals):
        if 'ho_dem' in vals or 'ten' in vals:
            for record in self:
                ho_dem = vals.get('ho_dem', record.ho_dem or '')
                ten = vals.get('ten', record.ten or '')
                vals['ma_dinh_danh'] = record._tao_ma_dinh_danh(ho_dem, ten)

        return super(NhanVien, self).write(vals)
    # =========================
    # THÔNG TIN CÔNG VIỆC CŨ
    # Giữ lại để Chấm công và Tính lương không bị lỗi
    # =========================
    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban'
    )

    chuc_vu_id = fields.Many2one(
        'chuc_vu',
        string='Chức vụ'
    )

    ngay_vao_lam = fields.Date(
        string='Ngày vào làm'
    )

    trang_thai_lam_viec = fields.Selection([
        ('dang_lam', 'Đang làm việc'),
        ('nghi_viec', 'Nghỉ việc'),
        ('tam_nghi', 'Tạm nghỉ'),
    ], string='Trạng thái làm việc', default='dang_lam')

    # =========================
    # THÔNG TIN LƯƠNG
    # Dùng cho module Tính lương
    # =========================
    luong_co_ban = fields.Float(
        string='Lương cơ bản'
    )

    phu_cap = fields.Float(
        string='Phụ cấp tháng'
    )

    ty_le_bao_hiem = fields.Float(
        string='Tỷ lệ bảo hiểm (%)',
        default=10.5
    )

    tien_bao_hiem = fields.Float(
        string='Tiền bảo hiểm',
        compute='_compute_luong_co_ban',
        store=True
    )

    tong_thu_nhap_co_ban = fields.Float(
        string='Tổng thu nhập cơ bản',
        compute='_compute_luong_co_ban',
        store=True
    )

    # =========================
    # TRƯỜNG MỞ RỘNG MỚI
    # Dùng cho chức năng Quản lý phòng ban, chức vụ, hợp đồng
    # =========================
    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban quản lý'
    )

    chuc_vu_id = fields.Many2one(
        'chuc_vu',
        string='Chức vụ quản lý'
    )

    hop_dong_ids = fields.One2many(
        'hop_dong_lao_dong',
        'nhan_vien_id',
        string='Hợp đồng lao động'
    )

    # =========================
    # LIÊN KẾT CŨ NẾU VIEW ĐANG CÓ
    # =========================
    lich_su_cong_tac_ids = fields.One2many(
        'lich_su_cong_tac',
        'nhan_vien_id',
        string='Lịch sử công tác'
    )

    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        'danh_sach_chung_chi_bang_cap',
        'nhan_vien_id',
        string='Danh sách chứng chỉ bằng cấp'
    )

    # =========================
    # COMPUTE
    # =========================
    @api.depends('ho_dem', 'ten')
    def _compute_ho_ten(self):
        for record in self:
            ho_dem = record.ho_dem or ''
            ten = record.ten or ''
            record.ho_ten = (ho_dem + ' ' + ten).strip()

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        today = fields.Date.today()
        for record in self:
            if record.ngay_sinh:
                record.tuoi = today.year - record.ngay_sinh.year
                if (today.month, today.day) < (record.ngay_sinh.month, record.ngay_sinh.day):
                    record.tuoi -= 1
            else:
                record.tuoi = 0

    @api.depends('tuoi')
    def _compute_so_nguoi_bang_tuoi(self):
        for record in self:
            if record.tuoi:
                domain = [('tuoi', '=', record.tuoi)]

                # Tránh lỗi NewId khi tạo nhân viên mới chưa lưu
                if record.id and isinstance(record.id, int):
                    domain.append(('id', '!=', record.id))

                records = self.env['nhan_vien'].search(domain)
                record.so_nguoi_bang_tuoi = len(records)
            else:
                record.so_nguoi_bang_tuoi = 0

    @api.depends('luong_co_ban', 'phu_cap', 'ty_le_bao_hiem')
    def _compute_luong_co_ban(self):
        for record in self:
            record.tien_bao_hiem = record.luong_co_ban * record.ty_le_bao_hiem / 100
            record.tong_thu_nhap_co_ban = record.luong_co_ban + record.phu_cap - record.tien_bao_hiem

    # =========================
    # ONCHANGE
    # =========================
    @api.onchange('chuc_vu_id')
    def _onchange_chuc_vu_id(self):
        for record in self:
            if record.chuc_vu_id:
                if record.chuc_vu_id.muc_luong_de_xuat:
                    record.luong_co_ban = record.chuc_vu_id.muc_luong_de_xuat

                if record.chuc_vu_id.phu_cap_chuc_vu:
                    record.phu_cap = record.chuc_vu_id.phu_cap_chuc_vu

    # =========================
    # RÀNG BUỘC
    # =========================
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError('Email không hợp lệ.')

    @api.constrains('tuoi')
    def _check_tuoi(self):
        for record in self:
            if record.tuoi and record.tuoi < 18:
                raise ValidationError('Nhân viên phải từ 18 tuổi trở lên.')

    @api.constrains('luong_co_ban', 'phu_cap', 'ty_le_bao_hiem')
    def _check_luong(self):
        for record in self:
            if record.luong_co_ban < 0:
                raise ValidationError('Lương cơ bản không được nhỏ hơn 0.')
            if record.phu_cap < 0:
                raise ValidationError('Phụ cấp không được nhỏ hơn 0.')
            if record.ty_le_bao_hiem < 0:
                raise ValidationError('Tỷ lệ bảo hiểm không được nhỏ hơn 0.')

    _sql_constraints = [
        ('unique_ma_dinh_danh', 'unique(ma_dinh_danh)', 'Mã định danh không được trùng!'),
        ('unique_email', 'unique(email)', 'Email không được trùng!'),
    ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []   
        if name:
                domain = [
                    '|', '|', '|',
                    ('ho_ten', operator, name),
                    ('ho_dem', operator, name),
                    ('ten', operator, name),
                    ('ma_dinh_danh', operator, name),
                ]

                records = self.search(domain + args, limit=limit)
        else:
                records = self.search(args, limit=limit)

        return records.name_get()
class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Lịch sử công tác'

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True,
        ondelete='cascade'
    )

    tu_ngay = fields.Date(
        string='Từ ngày'
    )

    den_ngay = fields.Date(
        string='Đến ngày'
    )

    vi_tri_cong_tac = fields.Char(
        string='Vị trí công tác'
    )

    phong_ban_cong_tac = fields.Char(
        string='Phòng ban công tác'
    )

    mo_ta = fields.Text(
        string='Mô tả'
    )


class DanhSachChungChiBangCap(models.Model):
    _name = 'danh_sach_chung_chi_bang_cap'
    _description = 'Danh sách chứng chỉ bằng cấp'

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True,
        ondelete='cascade'
    )

    ten_chung_chi = fields.Char(
        string='Tên chứng chỉ/bằng cấp'
    )

    don_vi_cap = fields.Char(
        string='Đơn vị cấp'
    )

    nam_cap = fields.Integer(
        string='Năm cấp'
    )

    ghi_chu = fields.Text(
        string='Ghi chú'
    )
