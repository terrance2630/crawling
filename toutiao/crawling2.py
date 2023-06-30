from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# 创建一个 WebDriver 实例，指定浏览器驱动的路径
driver = webdriver.Chrome()

# 打开网页
url = 'https://www.toutiao.com/article/7235891710436459063/?channel=&source=search_tab'
driver.get(url)
time.sleep(5)
# 等待页面加载完成
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# 获取页面内容
page_content = driver.page_source

with open('./data1.html', 'w', encoding='utf-8') as f:
    f.write(page_content)
print("源代码已保存")

# 关闭 WebDriver
driver.quit()
