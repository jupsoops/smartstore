from flask import Flask, request, jsonify
import json
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from cachetools import cached, TTLCache

app = Flask(__name__)

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
        # with open("result.txt", "w") as file:
        #     file.write(json.dumps(json_str))

        delivery_cnt = json.loads(json_str)
        # print(delivery_lead_times_dict)
        
        # 원하는 속성 가져오기
        # keptProducts
        # productDeliveryLeadTimes
        # productDailyDeliveryLeadTimes
        desired_attribute = delivery_cnt.get("product", {}).get("A", {}).get("productDailyDeliveryLeadTimes", {}).get("leadTimeCount")
        channel_name = delivery_cnt.get("product", {}).get("A", {}).get("channel", {}).get("channelName")
        if desired_attribute is None:
            return {"name": "null", "data": 0}
        
        return {"name": channel_name, "data": sum(desired_attribute)}
    
    except WebDriverException as e:
        print(f"An error occurred while crawling {url}: {str(e)}")
        return -1  # You can return a specific value to indicate an error
    
    
@app.route('/crawl', methods=['POST'])
def crawl_api():
    user_id = 'hanggon'
    data = request.get_json()  # POST로 전달된 JSON 데이터 추출
    urls = data.get('urls', [])  # JSON 데이터 내의 'urls' 키에 대한 값 추출
    urls_and_results = []
    results = {}

    for url in urls:
        result = crawl_data(url)
        results[url] = result

    urls_and_results.append(results)
    regdate = datetime.today().date().strftime("%Y-%m-%d")
    return jsonify(user_id=user_id, regdate=regdate, data=urls_and_results)

if __name__ == '__main__':
    app.run('0.0.0.0', 8800)
    #app.run()
