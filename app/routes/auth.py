from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, logout_user, current_user
from flask_bcrypt import check_password_hash, generate_password_hash  # Flask-Bcrypt의 함수 사용
from app import create_db_connection
from app.forms import LoginForm, RegistrationForm  # LoginForm과 RegistrationForm을 import합니다.
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # RegistrationForm을 인스턴스화합니다.

    if form.validate_on_submit():  # POST 요청에서 유효성을 검사합니다.
        email = form.email.data
        password = form.password.data

        # 데이터베이스 연결 생성
        connection = create_db_connection()
        cursor = connection.cursor()

        # 이메일이 이미 존재하는지 확인
        cursor.execute("SELECT * FROM users WHERE uemail = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email already exists. Please login.', 'warning')
            connection.close()
            return redirect(url_for('auth.login'))

        # 패스워드를 해싱하여 저장
        hashed_password = generate_password_hash(password).decode('utf-8')  # 해시를 문자열로 변환
        # 사용자 추가
        cursor.execute("INSERT INTO users (uemail, upw) VALUES (%s, %s)", (email, hashed_password))
        connection.commit()
        connection.close()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form) 

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # LoginForm을 인스턴스화합니다.

    if form.validate_on_submit():  # POST 요청에서 유효성을 검사합니다.
        email = form.email.data
        password = form.password.data

        # 데이터베이스 연결 생성
        connection = create_db_connection()
        cursor = connection.cursor()

        # 데이터베이스에서 사용자 정보 가져오기 (예제: users 테이블 사용)
        
        query = "SELECT uid, upw FROM users WHERE uemail = %s"
        cursor.execute(query, (email,))
        user_data = cursor.fetchone()

        if user_data:
            uid, hashed_password = user_data

            # 비밀번호 일치 확인
            if check_password_hash(hashed_password, password):
                # 사용자 객체 생성
                login_info = User(uid)
                # 사용자 객체를 session에 저장
                login_user(login_info, remember=True)


                flash('Logged in successfully.', 'success')
                return redirect(url_for('report.report'))
            else:
                flash('Incorrect password.', 'danger')
        else:
            flash('User not found with this email.', 'danger')

        cursor.close()
        connection.close()

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # 사용자 세션에서 로그인 상태 제거
    logout_user()

    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
