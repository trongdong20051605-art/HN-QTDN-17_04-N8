{
    'name': 'Quản lý Tính lương',
    'version': '1.0',
    'summary': 'Module quản lý tính lương nhân viên',
    'description': 'Tính lương dựa trên hồ sơ nhân sự và dữ liệu chấm công.',
    'category': 'Human Resources',
    'author': 'Student',
    'depends': ['base', 'nhan_su', 'cham_cong'],
    'data': [
        'security/ir.model.access.csv',
        'views/tinh_luong.xml',
        'views/bang_luong_thang.xml',
        'views/auto_tao_luong_view.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
