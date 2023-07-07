import concurrent.futures
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime  
import json

DIR = "yiche/"

firefox_options = Options()
#firefox_options.add_argument('--headless')
firefox_options.set_preference('permissions.default.image', 2)  # 禁止加载图片
firefox_options.set_preference('dom.webdriver.enabled', False)
firefox_options.set_preference('javascript.enabled', False)
firefox_options.set_preference('webdriver.load.strategy', 'unstable')
firefox_options.set_preference('browser.download.manager.showWhenStarting', False)

def scrape_yiche_page_info(url):
    try:
        with webdriver.Firefox(options=firefox_options) as driver:
            driver.set_page_load_timeout(60)  # 设置超时限制
            driver.get(url)
            time.sleep(3)  # 延迟访问
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            comment_number = soup.find('li', class_='news-detail-position-pinglun').find('a').text.strip()
            like_number = soup.find('li', class_='news-detail-position-dianzan').find('a').text.strip()

            authors = soup.find_all('div', class_='author-box')
            author_list = []
            for author in authors:
                author_id = author.find('a', class_='button attention-button').get('data-id')
                author_list.append({
                    '作者名字': author.find('p', class_='author-name').text.strip(),
                    '作者ID': author_id,
                    '作者主页': f"https://i.yiche.com/u{author_id}/!article/"
                })

            return {
                '平台': "易车",
                '评论数': comment_number,
                '点赞数': like_number,
                '作者列表': author_list,
                "文章": url
            }
    except Exception as e:
        print("易车在爬取过程中出现错误:", e)
        return None


def scrape_yiche_urls(urls, title):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        with tqdm(total=len(urls), desc="易车进度") as pbar:
            for url in urls:
                result = scrape_yiche_page_info(url)
                if result:
                    with open(DIR + title + ".json", 'a', encoding='utf-8') as f:
                        f.write(json.dumps(result, ensure_ascii=False))
                        f.write("\n")  # Add a newline to separate each entry
                pbar.update(1)


def main():
    title = "yiche_data" + str(datetime.now().strftime("%m-%d-%H-%M"))

    # 从文件中读取url
    with open(DIR + 'yiche_url.txt', 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    # 抓取页面信息
    scrape_yiche_urls(urls, title)


if __name__ == "__main__":
    main()
