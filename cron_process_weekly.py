import mysql.connector
import json
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from cachetools import cached, TTLCache
import time

# MySQL 연결 설정
db_config = {
    "user": "axissoft",
    "password": "axis7!73450",
    "host": "49.50.164.157",
    "database": "store"
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

cache = TTLCache(maxsize=100, ttl=3600)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

@cached(cache)
def crawl_data(url):
    try:
        driver.get(url)

        wait = WebDriverWait(driver, 1)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "detail_viewer")))

        js_code = 'return JSON.stringify(__PRELOADED_STATE__);'
        json_str = driver.execute_script(js_code)

        delivery_cnt = json.loads(json_str)
        
        desired_attribute = delivery_cnt.get("product", {}).get("A", {}).get("productDailyDeliveryLeadTimes", {}).get("leadTimeCount")
        channel_name = delivery_cnt.get("product", {}).get("A", {}).get("channel", {}).get("channelName")
        if desired_attribute is None:
            return {"name": "null", "data": 0}
        
        return {"name": channel_name, "data": sum(desired_attribute)}
    
    except WebDriverException as e:
        print(f"An error occurred while crawling {url}: {str(e)}")
        return {"name": "error", "data": -1}  # You can return a specific value to indicate an error

def process_data():
    #로그에 기록 남기기
    current_datetime = datetime.now()
    start_time = time.time()  # 실행 시간 측정 시작 시간 기록
    # 현재 날짜와 시간을 문자열로 변환하고 출력
    print("====================== Current Date : ", current_datetime.strftime('%Y-%m-%d %H:%M:%S'), "======================")

    # cursor.execute("SELECT uid, purl FROM product WHERE uid = 'jups'")
    cursor.execute("SELECT pid, uid, purl, pname FROM product where 1 = 1")
    product_list = cursor.fetchall()

    #매주돌릴때
    today = datetime.today().date()
    year, month, day = today.year, today.month, today.day
    date_obj = datetime(year, month, day)
    year, week_number, weekday = date_obj.isocalendar()


    week_number -= (datetime(year, month, 1).isocalendar()[1] - 1)
    repdate = f"{year}{month:02d}-{week_number}"

    success_count = 0  # 성공한 항목 카운터 초기화
    for item in product_list:
        data = crawl_data(item[2])  # item[2] contains purl

        if data != -1:
            insert_query = "INSERT INTO report (uid, repdate, pid, delivery) VALUES (%s, %s, %s, %s)"
            values = (item[1], repdate, item[0], data["data"]) 
            success_count += 1

            try:
                cursor.execute(insert_query, values)
                conn.commit()
            except Exception as e:
                conn.rollback()  # 롤백 처리
                print(f"[{item[1]}-{item[0]}] An error occurred while executing SQL query: {str(e)}")
                # 다른 오류 처리 작업 수행 가능

    end_time = time.time()  # 실행 시간 측정 종료 시간 기록
    execution_time = end_time - start_time  # 실행 시간 계산
    print("Execution Time:", execution_time, "seconds")
    print("total : ",len(product_list), " success : ", success_count)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    process_data()
