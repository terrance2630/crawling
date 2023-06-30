from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

url = "https://www.toutiao.com/article/7235891710436459063/?channel=&source=search_tab"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

try:
    # 等待指定的元素出现
    element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#root > div.article-detail-container > div.left-sidebar > div > div:nth-child(2) > div")
        )
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    with open("./xhs.html", 'w') as f:
        f.write(driver.page_source)
        # 关闭浏览器驱动

    # 找到并打印点赞数量
    like_count_div = soup.find('div', class_='digg-icon')
    like_count = like_count_div.find_next_sibling('span').text
    print(f"点赞数量：{like_count}")

    # 找到并打印评论数量
    comment_count_div = soup.find('div', class_='detail-interaction-comment')
    comment_count = comment_count_div.find('span').text
    print(f"评论数量：{comment_count}")

    # 找到并打印用户主页和用户名
    user_meta_div = soup.find('div', class_='article-meta')
    user_name_span = user_meta_div.find('span', class_='name')
    user_homepage = 'www.toutiao.com/'+user_name_span.find('a')['href']
    user_name = user_name_span.text.strip()
    print(f"用户主页：{user_homepage}")
    print(f"用户名：{user_name}")

finally:
    driver.quit()
