# Task Manager

Ứng dụng quản lý công việc được xây dựng bằng Flask, cho phép người dùng tạo và quản lý các công việc của mình.

## Tính năng

- **Xác thực người dùng**:
  - Đăng ký tài khoản mới
  - Đăng nhập/Đăng xuất
  - Hỗ trợ vai trò admin

- **Quản lý công việc**:
  - Thêm công việc mới
  - Đánh dấu công việc đã hoàn thành
  - Xóa công việc
  - Theo dõi thời gian tạo và hoàn thành
  - Đặt hạn chót cho công việc

- **Tính năng cho Admin**:
  - Xem tất cả công việc của mọi người dùng
  - Xóa bất kỳ công việc nào

- **Tính năng người dùng**:
  - Cập nhật thông tin cá nhân
  - Thay đổi avatar
  - Quản lý email

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package installer)
- Các thư viện Python được liệt kê trong file requirements.txt

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd task-manager
```

2. Chạy file setup.bat:
```bash
setup.bat
```

File setup.bat sẽ tự động:
- Tạo môi trường ảo Python
- Cài đặt các gói phụ thuộc
- Tạo các thư mục cần thiết
- Tạo tài khoản admin mặc định

## Sử dụng

1. Kích hoạt môi trường ảo:
```bash
call venv\Scripts\activate.bat
```

2. Chạy ứng dụng:
```bash
python task_manager\app.py
```

3. Truy cập ứng dụng tại: http://localhost:5000

## Tài khoản mặc định

- **Admin**:
  - Username: admin
  - Password: admin123

## Cấu trúc thư mục

```
task_manager/
├── app.py              # File chính của ứng dụng
├── database/           # Thư mục chứa database
├── static/            
│   └── images/        # Thư mục chứa ảnh avatar
└── templates/         # Các file template HTML
```

## Công nghệ sử dụng

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: 
  - HTML/CSS
  - Bootstrap 5
  - Font Awesome
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **Database ORM**: SQLAlchemy 