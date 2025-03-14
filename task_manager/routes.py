from app import app, db, User, Task, get_random_avatar, count_overdue_tasks
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    overdue_count = count_overdue_tasks(current_user)
    return render_template('index.html', tasks=tasks, overdue_count=overdue_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        avatar_url = get_random_avatar()
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, avatar=avatar_url)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/task/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    due_date = request.form.get('due_date')
    if title and due_date:
        due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
        task = Task(title=title, user_id=current_user.id, due_date=due_date)
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>/complete')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.status = 'completed'
        task.finished = datetime.utcnow()
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>/delete')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id or current_user.is_admin:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index')) 