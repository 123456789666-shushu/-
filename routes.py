from flask import render_template, url_for, flash, redirect, request, abort
from app import app
from extensions import db
from models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# 主页
@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts)

# 注册
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        role = request.form['role']
        
        # 检查昵称是否已存在
        user = User.query.filter_by(nickname=nickname).first()
        if user:
            flash('昵称已被使用，请选择其他昵称', 'danger')
            return redirect(url_for('register'))
        
        # 处理头像上传
        avatar = 'default.jpg'
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file.filename != '':
                filename = secure_filename(file.filename)
                # 确保文件名唯一
                filename = f"{nickname}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                avatar = filename
        
        # 创建新用户
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(nickname=nickname, password=hashed_password, role=role, avatar=avatar)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# 登录
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        
        user = User.query.filter_by(nickname=nickname).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('登录失败，请检查昵称和密码', 'danger')
    return render_template('login.html')

# 登出
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# 创建帖子
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        
        flash('帖子发布成功！', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html')

# 帖子详情
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# 添加评论
@app.route("/post/<int:post_id>/comment", methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    
    comment = Comment(content=content, author=current_user, post=post)
    db.session.add(comment)
    db.session.commit()
    
    flash('评论发布成功！', 'success')
    return redirect(url_for('post', post_id=post_id))

# 后台管理
@app.route("/admin")
@login_required
def admin():
    if not current_user.is_developer:
        abort(403)
    
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    
    return render_template('admin.html', total_users=total_users, total_posts=total_posts, total_comments=total_comments)

# 删除帖子
@app.route("/admin/delete_post/<int:post_id>")
@login_required
def delete_post(post_id):
    if not current_user.is_developer:
        abort(403)
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    flash('帖子已删除', 'success')
    return redirect(url_for('admin'))

# 删除评论
@app.route("/delete_comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # 只有评论作者或开发者可以删除评论
    if not (current_user.is_developer or comment.author == current_user):
        abort(403)
    
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    
    flash('评论已删除', 'success')
    return redirect(url_for('post', post_id=post_id))

# 初始化开发者账号
@app.route("/init_developers")
def init_developers():
    # 创建5名开发者账号
    developers = [
        {'nickname': 'dev1', 'password': 'dev123', 'role': 'parent'},
        {'nickname': 'dev2', 'password': 'dev123', 'role': 'child'},
        {'nickname': 'dev3', 'password': 'dev123', 'role': 'parent'},
        {'nickname': 'dev4', 'password': 'dev123', 'role': 'child'},
        {'nickname': 'dev5', 'password': 'dev123', 'role': 'parent'}
    ]
    
    for dev in developers:
        user = User.query.filter_by(nickname=dev['nickname']).first()
        if not user:
            hashed_password = generate_password_hash(dev['password'], method='pbkdf2:sha256')
            user = User(nickname=dev['nickname'], password=hashed_password, role=dev['role'], is_developer=True)
            db.session.add(user)
    
    db.session.commit()
    flash('开发者账号初始化完成', 'success')
    return redirect(url_for('home'))