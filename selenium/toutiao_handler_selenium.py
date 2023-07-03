import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')

def scrape_toutiao_page_info(url):
    with webdriver.Chrome(options=chrome_options) as driver:
        try:
            driver.get(url)
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#root > div.article-detail-container > div.left-sidebar > div > div:nth-child(2) > div")
                )
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            like_count = soup.find('div', class_='digg-icon').find_next_sibling('span').text
            comment_count = soup.find('div', class_='detail-interaction-comment').find('span').text
            user_name_span = soup.find('div', class_='article-meta').find('span', class_='name')
            user_homepage = 'www.toutiao.com/'+user_name_span.find('a')['href']
            user_name = user_name_span.text.strip()

            return {
                '平台': "头条",
                '评论数': comment_count,
                '点赞数': like_count,
                '用户名': user_name,
                '用户主页': user_homepage,
                "文章": url
            }

        except Exception as e:
            print("头条在爬取过程中出现错误:", e)
            return None


def scrape_toutiao_urls(urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(scrape_toutiao_page_info, urls), total=len(urls), desc="头条进度"))
    return [result for result in results if result]  # 过滤掉None值
