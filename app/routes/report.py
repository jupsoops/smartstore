from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from collections import OrderedDict
from app import create_db_connection

report_bp = Blueprint('report', __name__)

@report_bp.route('/report', methods=['GET'])
@login_required
def report():
    # MySQL 연결 생성
    connection = create_db_connection()
    cursor = connection.cursor()

    # MySQL에서 데이터 가져오기
    viewtype = request.args.get('vi', default='daily')

    if viewtype == "weekly":
        repdate_title = "week"
        query = "SELECT a.repdate, concat(b.sort, '. ', b.pname) as pname, b.purl, a.delivery \
                FROM report a left join product b on a.pid = b.pid where a.uid = %s ORDER BY a.repdate, b.sort"
    else:
        repdate_title = "date"
        query = "SELECT a.repdate, concat(b.sort, '. ', b.pname) as pname, b.purl, a.delivery \
                FROM report_daily a left join product b on a.pid = b.pid where a.uid = %s ORDER BY a.repdate, b.sort"

    
    cursor.execute(query, (current_user.id,))
    data = cursor.fetchall()

    # 피봇 생성
    pivot_data = {}
    purls = []

    for row in data:
        repdate, pname, purl, delivery = row
        purls.append(pname + "|" + purl)
        
        if (repdate) not in pivot_data:
            pivot_data[repdate] = {}
            
        pivot_data[repdate][pname + "|" + purl] = {"data": int(delivery), "diff":0}

    purls_unique = list(OrderedDict.fromkeys(purls))

    prev_week_data = None  # 이전 주차 데이터 초기화
    # 두 번째 반복문에서 diff 값 계산 및 저장
    for repdate, values in pivot_data.items():
        if prev_week_data:
            for purl, value in values.items():
                prev_value = prev_week_data.get(purl)
                if prev_value is not None:
                    diff = value["data"] - prev_value["data"]
                    value["diff"] = diff
                else:
                    value["diff"] = 0

        prev_week_data = values.copy()

    # MySQL 연결 종료
    cursor.close()
    connection.close()

    return render_template('report.html', umail=current_user.useremail,pivot_data=pivot_data, purls=purls_unique, repdate_title=repdate_title, viewType=viewtype)
