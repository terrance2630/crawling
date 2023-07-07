import concurrent.futures
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

firefox_options = Options()
firefox_options.add_argument('--headless')
firefox_options.set_preference('permissions.default.image', 2)  # 禁止加载图片

def scrape_yiche_page_info(url):
    try:
        with webdriver.Firefox(options=firefox_options) as driver:
            driver.get(url)
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


def scrape_yiche_urls(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(scrape_yiche_page_info, urls))
    return [result for result in results if result]  # 过滤掉None值
