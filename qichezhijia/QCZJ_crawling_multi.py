import json
import concurrent.futures
from selenium import webdriver
from bs4 import BeautifulSoup

def scrape_page_info(url):
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
        
        author_homepage = author_link['href'] if author_link else "未找到作者主页链接"
        author_title = author_link['title'] if author_link else "未找到作者标题"

        driver.quit()
        
        return view_number, reply_number, author_homepage, praise_number, author_title

    except Exception as e:
        print("在爬取过程中出现错误:", e)
        driver.quit()
        return None, None, None, None, None


def scrape_multiple_urls(urls):
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_page_info, url) for url in urls]

        for future, url in zip(futures, urls):
            view_number, reply_number, author_homepage, praise_number, author_title = future.result()

            if all([view_number, reply_number, author_homepage, praise_number, author_title]):
                temp = {
                    "平台": "汽车之家",
                    "浏览量": view_number,
                    "回复量": reply_number,
                    "点赞量": praise_number,
                    "作者主页": author_homepage,
                    "作者": author_title
                }
                result.append(temp)
                print(f"{author_title}的数据已保存")
            else:
                print(f"无法成功爬取 {url} 的页面信息。")
                print([view_number, reply_number, author_homepage, praise_number, author_title])

    with open('./data.json', 'w', encoding="utf8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        print("数据已保存到 data.json 文件")


urls = [
    'https://club.autohome.com.cn/bbs/thread-c-3495-105732139-1.html',
    'https://club.autohome.com.cn/bbs/thread-c-3495-105715932-1.html',
    'https://club.autohome.com.cn/bbs/thread-c-6960-105709282-1.html'
]

scrape_multiple_urls(urls)
