import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup



url = "https://smartstore.naver.com/biichnalda/products/5614226949"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

wait = WebDriverWait(driver, 1)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "detail_viewer")))

soup = BeautifulSoup(driver.page_source, "html.parser")

driver.quit()

detail_viewer = soup.find("div", class_="detail_viewer")

if detail_viewer:
    second_div = detail_viewer.find_all("div", recursive=False)[1]
    ul = second_div.find("ul")
    if ul:
        li_items = ul.find_all("li")
        total_sum = 0
        
        for li in li_items:
            em_text = li.find("em").find("strong").get_text()
            numbers = re.findall(r'\d+', em_text)
            
            for num in numbers:
                total_sum += int(num)
        
        print(numbers) 
        print(total_sum) 
    else:
        print("err") 
else:
    print("err2")