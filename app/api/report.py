# app/routes/api.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from collections import OrderedDict
from app import create_db_connection

api_bp = Blueprint('api', __name__)

# MySQL 연결 생성
connection = create_db_connection()
cursor = connection.cursor()

# API 엔드포인트를 보호하려면 login_required 데코레이터를 사용합니다.

@api_bp.route('/api/report', methods=['GET'])
@login_required
def get_report_data():
    viewtype = request.args.get('vi', default='daily')

    if viewtype == "weekly":
        query = "SELECT a.repdate, a.pid, concat(b.sort, '. ', b.pname) as pname, b.purl, a.delivery \
                FROM report a left join product b on a.pid = b.pid where a.uid = %s ORDER BY a.repdate, b.sort"
    else:
        query = "SELECT a.repdate, a.pid, concat(b.sort, '. ', b.pname) as pname, b.purl, a.delivery \
                FROM report_daily a left join product b on a.pid = b.pid where a.uid = %s ORDER BY a.repdate, b.sort"

    cursor.execute(query, (current_user.id,))
    data = cursor.fetchall()

    # 피봇 생성
    pivot_data = {}
    purls = []

    store = {}

    for row in data:
        repdate, pid, pname, purl, delivery = row
        #################################### 레포트 형  ####################################
        purls.append(pname + "|" + purl)
        
        if (repdate) not in pivot_data:
            pivot_data[repdate] = {}
            
        pivot_data[repdate][pname + "|" + purl] = {"data": int(delivery), "diff":0}
        #################################### 레포트 형  ####################################

        if (pid) not in store:
            store[pid] = {}

        # store[pid] = delivery

        store[pid][repdate] = {"data": int(delivery), "name":pname, "repdate":repdate}

    # purls_unique = list(OrderedDict.fromkeys(purls))

    # # 중복제거하고 다시 루프 돌려서 이전 row 차이값 계산
    # prev_week_data = None  # 이전 row 데이터 초기화
    # for repdate, values in pivot_data.items():
    #     if prev_week_data:
    #         for purl, value in values.items():
    #             prev_value = prev_week_data.get(purl)
    #             if prev_value is not None:
    #                 diff = value["data"] - prev_value["data"]
    #                 value["diff"] = diff
    #             else:
    #                 value["diff"] = 0

    #     prev_week_data = values.copy()

    # print(pivot_data)
    # print(purls)

    return jsonify(store)
