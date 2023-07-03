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
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#root > div.article-detail-container > div.left-sidebar > div > div:nth-child(2) > div")
            )
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 找到并打印点赞数量
        like_count_div = soup.find('div', class_='digg-icon')
        like_count = like_count_div.find_next_sibling('span').text

        # 找到并打印评论数量
        comment_count_div = soup.find('div', class_='detail-interaction-comment')
        comment_count = comment_count_div.find('span').text

        # 找到并打印用户主页和用户名
        user_meta_div = soup.find('div', class_='article-meta')
        user_name_span = user_meta_div.find('span', class_='name')
        user_homepage = 'www.toutiao.com/'+user_name_span.find('a')['href']
        user_name = user_name_span.text.strip()

        driver.quit()

        result = {
            '平台': "头条",
            '评论数': comment_count,
            '点赞数': like_count,
            '用户名': user_name,
            '用户主页': user_homepage,
            "文章": url
        }

        return result

    except Exception as e:
        print("头条在爬取过程中出现错误:", e)
        driver.quit()
        return None


def scrape_toutiao_urls(urls):
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_toutiao_page_info, url) for url in urls]

        with tqdm(total=len(futures), desc="头条进度") as pbar:
            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())
                pbar.update(1)

    return result
