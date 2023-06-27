import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def scrape_page_info(url):
    # 创建 Chrome WebDriver，并传入 ChromeOptions 和驱动路径
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    try:
        # 访问目标网页
        driver.get(url)
        


        # 获取页面源代码
        page_source = driver.page_source
        
        # 从页面源代码中提取数据
        soup = BeautifulSoup(page_source, 'html.parser')
        
        with open("./xhs.html", 'w') as f:
            f.write(page_source)
        # 关闭浏览器驱动
        driver.quit()
        
        return "done"

    except Exception as e:
        print("在爬取过程中出现错误:", e)
        driver.quit()
        return "None, None, None, None, None"

url = 'https://www.xiaohongshu.com/explore/64884937000000000800f53a?m_source=baidusem'

print(scrape_page_info(url))