from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Tạo đường dẫn tuyệt đối đến file database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'task_manager.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200))
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created = db.Column(db.DateTime, default=datetime.utcnow)
    finished = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_random_avatar():
    # Tạo avatar từ API mới
    username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2)).upper()  # Lấy 2 chữ cái viết hoa
    avatar_url = f"https://avatar.iran.liara.run/username?username={username}"
    return avatar_url

def count_overdue_tasks(user):
    now = datetime.utcnow()
    return Task.query.filter_by(user_id=user.id).filter(
        Task.due_date < now,
        Task.status != 'completed'
    ).count()

def to_vietnam_timezone(utc_time):
    if utc_time is None:
        return None
    return utc_time + timedelta(hours=7)

def is_admin():
    return current_user.is_authenticated and current_user.is_admin

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    overdue_count = count_overdue_tasks(current_user)
    now = datetime.utcnow()
    
    # Nếu là admin, lấy tất cả công việc của mọi người dùng
    if is_admin():
        tasks = Task.query.join(User).all()
    
    # Chuyển đổi thời gian của tất cả các task sang múi giờ Việt Nam
    for task in tasks:
        task.created = to_vietnam_timezone(task.created)
        task.finished = to_vietnam_timezone(task.finished)
        task.due_date = to_vietnam_timezone(task.due_date)
    
    return render_template('index.html', tasks=tasks, overdue_count=overdue_count, now=to_vietnam_timezone(now), is_admin=is_admin())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại')
            return redirect(url_for('register'))
            
        # Sử dụng username thực tế cho avatar
        avatar_url = f"https://avatar.iran.liara.run/username?username={username}"
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, avatar=avatar_url)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Đăng ký thành công! Vui lòng đăng nhập')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        due_date_str = request.form.get('due_date')
        
        if not title:
            flash('Tiêu đề không được để trống')
            return redirect(url_for('add_task'))
            
        try:
            # Chuyển đổi thời gian từ form (đã ở múi giờ địa phương) sang UTC để lưu vào database
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') - timedelta(hours=7) if due_date_str else None
        except ValueError:
            flash('Định dạng ngày không hợp lệ')
            return redirect(url_for('add_task'))
            
        new_task = Task(
            title=title,
            due_date=due_date,
            user_id=current_user.id,
            created=datetime.utcnow()
        )
        
        db.session.add(new_task)
        db.session.commit()
        flash('Thêm công việc mới thành công!')
        return redirect(url_for('index'))
    
    overdue_count = count_overdue_tasks(current_user)
    return render_template('add_task.html', overdue_count=overdue_count)

@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('Bạn không có quyền thực hiện hành động này')
        return redirect(url_for('index'))
    
    task.status = 'completed'
    task.finished = datetime.utcnow()
    db.session.commit()
    flash('Đã đánh dấu công việc là hoàn thành!')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # Kiểm tra username đã tồn tại chưa
        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại')
            return redirect(url_for('profile'))
            
        # Kiểm tra email đã tồn tại chưa
        if email:  # Chỉ kiểm tra nếu email không rỗng
            if email != current_user.email and User.query.filter_by(email=email).first():
                flash('Email đã được sử dụng')
                return redirect(url_for('profile'))
        else:
            email = None  # Đặt email là None nếu trường email rỗng
            
        # Xử lý upload avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                # Đảm bảo tên file an toàn
                filename = secure_filename(file.filename)
                # Tạo tên file duy nhất bằng cách thêm timestamp
                _, ext = os.path.splitext(filename)
                new_filename = f"avatar_{current_user.id}_{int(datetime.utcnow().timestamp())}{ext}"
                
                # Lưu file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(file_path)
                
                # Cập nhật đường dẫn avatar trong database
                current_user.avatar = url_for('static', filename=f'images/{new_filename}')
        
        # Cập nhật thông tin người dùng
        current_user.username = username
        current_user.email = email  # Email có thể là None
        db.session.commit()
        
        flash('Cập nhật thông tin thành công!')
        return redirect(url_for('profile'))
    
    overdue_count = count_overdue_tasks(current_user)
    return render_template('profile.html', overdue_count=overdue_count)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Kiểm tra quyền: chỉ admin mới có thể xóa task của người khác
    if not is_admin() and task.user_id != current_user.id:
        flash('Bạn không có quyền thực hiện hành động này')
        return redirect(url_for('index'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Đã xóa công việc thành công!')
    return redirect(url_for('index'))

def create_admin():
    # Kiểm tra xem admin đã tồn tại chưa
    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            is_admin=True,
            avatar="https://avatar-placeholder.iran.liara.run/public"
        )
        db.session.add(admin)
        db.session.commit()
        print("Tài khoản admin đã được tạo thành công!")
    else:
        print("Tài khoản admin đã tồn tại!")

with app.app_context():
    db.create_all()
    create_admin()  # Tự động tạo admin khi khởi động

if __name__ == '__main__':
    app.run(debug=True) 