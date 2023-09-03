from flask import Flask, request, jsonify
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
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
    
    driver.get(url)

    wait = WebDriverWait(driver, 1)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "detail_viewer")))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # driver.quit()
    
    detail_viewer = soup.find("div", class_="detail_viewer")
    
    if detail_viewer:
        second_div = detail_viewer.find_all("div", recursive=False)[1]
        ul = second_div.find("ul")
        if ul:
            li_items = ul.find_all("li")
            total_sum = 0
            
            for li in li_items:
                em_element = li.find("em")
                strong_element = None

                try:
                    strong_element = em_element.find("strong")
                except AttributeError:
                    pass  # strong_element가 없을 때의 예외 처리

                if strong_element:
                    em_text = strong_element.get_text()
                    numbers = re.findall(r'\d+', em_text)
                    for num in numbers:
                        total_sum += int(num)
           
            return total_sum
        else:
            return 0
    else:
        return 0

@app.route('/crawl', methods=['POST'])
def crawl_api():
    data = request.get_json()  # POST로 전달된 JSON 데이터 추출
    urls = data.get('urls', [])  # JSON 데이터 내의 'urls' 키에 대한 값 추출
    results = {}

    for url in urls:
        result = crawl_data(url)
        results[url] = result

    return jsonify(results)

if __name__ == '__main__':
    app.run()
