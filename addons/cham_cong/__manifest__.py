{
    'name': 'Quản lý Chấm công',
    'version': '1.0',
    'summary': 'Module quản lý chấm công nhân viên',
    'description': 'Quản lý chấm công, giờ vào, giờ ra, giờ làm thêm và trạng thái làm việc của nhân viên.',
    'category': 'Human Resources',
    'author': 'Student',
    'depends': ['base', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/cham_cong.xml',
        'views/bang_cong_thang.xml',
        'views/canh_bao_cham_cong.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}

