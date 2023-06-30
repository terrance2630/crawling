import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')

def scrape_yiche_page_info(url):


    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        page_content = driver.page_source

        soup = BeautifulSoup(page_content, 'html.parser')

        comment_element = soup.find('li', class_='news-detail-position-pinglun')
        comment_number = comment_element.find('a').text.strip()

        like_element = soup.find('li', class_='news-detail-position-dianzan')
        like_number = like_element.find('a').text.strip()

        authors = soup.find_all('div', class_='author-box')

        author_list = []
        for author in authors:
            author_name = author.find('p', class_='author-name').text.strip()
            author_id = author.find('a', class_='button attention-button').get('data-id')
            author_homepage = f"https://i.yiche.com/u{author_id}/!article/"

            author_info = {
                '作者名字': author_name,
                '作者ID': author_id,
                '作者主页': author_homepage
            }
            author_list.append(author_info)

        driver.quit()

        result = {
            '平台': "易车",
            '评论数': str(comment_number),
            '点赞数': str(like_number),
            '作者列表': str(author_list),
            "文章": str(url)
        }

        return result

    except Exception as e:
        print("易车在爬取过程中出现错误:", e)
        driver.quit()
        return None


def scrape_yiche_urls(urls):
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_yiche_page_info, url) for url in urls]

        with tqdm(total=len(futures), desc="易车进度") as pbar:
            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())
                pbar.update(1)

    return result

