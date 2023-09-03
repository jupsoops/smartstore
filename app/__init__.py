from flask import Flask
from flask_login import LoginManager
from app.models import User
import mysql.connector


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# MySQL 연결 설정
db_config = {
    "user": "axissoft",
    "password": "axis7!73450",
    "host": "49.50.164.157",
    "database": "store"
}

# MySQL 연결 함수
def create_db_connection():
    return mysql.connector.connect(**db_config)


login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(uid):
    print("load_user:",uid)
    connection = create_db_connection()  # 데이터베이스 연결 함수 (이전 답변에서 정의한 함수)
    cursor = connection.cursor()

    query = "SELECT uid, uemail FROM users WHERE uid = %s"
    cursor.execute(query, (uid,))
    user_data = cursor.fetchone()

    if user_data:
        uid, uemail = user_data
        user = User(uid)  # User 모델로 사용자 객체 생성
        user.useremail = uemail  # 사용자 객체에 추가 정보 할당
        return user

    return None  # 사용자가 없을 경우 None 반환


from app.api.report import api_bp
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.report import report_bp  # report 블루프린트를 임포트

app.register_blueprint(api_bp)
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(report_bp)  # report 블루프린트를 등록