import concurrent.futures
from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm


def scrape_autohome_page_info(url):
    driver = webdriver.Chrome()

    try:
        driver.get(url)
        page_source = driver.page_source
        
        

        soup = BeautifulSoup(page_source, 'html.parser')

        view_span = soup.select_one('.post-handle-view strong')
        reply_span = soup.select_one('.post-handle-reply strong')
        praise_span = soup.select_one('.post-assist-praise strong')
        author_link = soup.select_one('.user-name a')

        

        view_number = view_span.text if view_span else '0'
        reply_number = reply_span.text if reply_span else '0'
        praise_number = praise_span.text if praise_span and praise_span.text else '0'
        with open(f'{view_number}.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        author_homepage = author_link['href'] if author_link else "未找到作者主页链接"
        author_title = author_link['title'] if author_link else "未找到作者标题"

        driver.quit()

        temp = {
            "平台": "汽车之家",
            "浏览量": view_number,
            "回复量": reply_number,
            "点赞量": praise_number,
            "作者主页": author_homepage,
            "作者": author_title
        }

        return temp

    except Exception as e:
        print("在爬取过程中出现错误:", e)
        driver.quit()
        return None


def scrape_autohome_urls(urls):
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_autohome_page_info, url) for url in urls]

        with tqdm(total=len(futures), desc="汽车之家进度") as pbar:
            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())
                pbar.update(1)

    return result
