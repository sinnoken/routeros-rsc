import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# 從環境變數讀取 Chrome 路徑
chrome_path = os.getenv('CHROME_PATH')  # 這是從 GitHub Actions 中傳遞過來的
chromedriver_path = os.getenv('CHROMEDRIVER_PATH')  # 這是從 GitHub Actions 中傳遞過來的
print(f"Chrome Path: {chrome_path}")
print(f"ChromeDriver Path: {chromedriver_path}")

# 設定 Chrome 瀏覽器
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 無頭模式
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 指定 Chrome 瀏覽器的路徑
options.binary_location = chrome_path

# 指定 ChromeDriver 路徑
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)
#driver = webdriver.Chrome(service=chromedriver_path, options=options)


url = "https://internet-measurement.com/#ips"
url = "https://disp.cc/b/"
css_selector = "#ips > pre:nth-child(1)"
css_selector = ".disp_bbs"

driver.get(url)

# 使用 CSS Selector 定位元素
element = driver.find_element(By.CSS_SELECTOR, css_selector)
print(element.text)  # 取出元素內的文本

driver.quit()
