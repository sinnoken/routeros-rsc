from selenium import webdriver
from selenium.webdriver.common.by import By

# 設定 Chrome 瀏覽器
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 無頭模式
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

url = "https://internet-measurement.com/#ips"
driver.get(url)

# 使用 CSS Selector 定位元素
element = driver.find_element(By.CSS_SELECTOR, "#ips > pre:nth-child(1)")
print(element.text)  # 取出元素內的文本

driver.quit()
