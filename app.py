from flask import Flask
import os
from extensions import db, login_manager

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 初始化扩展
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 导入模型和路由
from models import *
from routes import *

# 运行应用
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
