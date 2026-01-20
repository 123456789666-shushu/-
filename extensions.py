from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 创建扩展实例，但不初始化
db = SQLAlchemy()
login_manager = LoginManager()