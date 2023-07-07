import asyncio
import json
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from datetime import datetime  
from concurrent.futures import TimeoutError
from tqdm import tqdm
import random
import re
from datetime import datetime  


DIR = "autohome/"

# 创建正则表达式对象
autohome_pattern = re.compile(r"(www\.)?autohome\.com\.cn")
firefox_options = Options()
firefox_options.set_preference('permissions.default.image', 2)  # 禁止加载图片

def get_text(element):
    return element.text.strip() if element and element.text.strip() else '0'

def scrape_autohome_page_info(url):
    with webdriver.Firefox(options=firefox_options) as driver:
        try:
            #driver.minimize_window()
            driver.get(url)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            view_number = soup.select_one('.post-handle-view strong')
            reply_number = soup.select_one('.post-handle-reply strong')
            praise_number = soup.select_one('.post-assist-praise strong')

            script_tags = soup.find_all('script')
            for script_tag in script_tags:
                script_content = script_tag.string
                if script_content and '__TOPICINFO__' in script_content:
                    topic_member_id = script_content.split("topicMemberId: ",1)[1].split(",")[0].strip()
                    topic_member_name = script_content.split("topicMemberName: '",1)[1].split("'")[0]

            result = {
                "平台": "汽车之家",
                "浏览数": get_text(view_number),
                "评论数": get_text(reply_number),
                "点赞数": get_text(praise_number),
                "加精推荐": 'True' if any(soup.find_all('div', class_='stamp orange activate')) else 'False',
                "用户id": topic_member_id,
                "用户名": topic_member_name,
                "文章": url
            }
            return result

        except Exception as e:
            print("汽车之家在爬取过程中出现错误:", e)
            return None
        
async def process_url(url, title):
    # 检查 URL 是否匹配正则表达式
    if not autohome_pattern.search(url):
        return

    try:
        result = await loop.run_in_executor(None, scrape_autohome_page_info, url)
        if result:  # 确保结果不是空的
            with open(title, 'a', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False)
                f.write('\n')
    except (Exception, TimeoutError):  # 捕获所有的异常包括超时异常
        print(f"Error occurred while processing url {url}")
    finally:
        await asyncio.sleep(random.uniform(1.0, 3.0))  # 随机等待1到3秒
        return


async def main():
    # 从外部文件读取URLs
    with open(DIR+"autohome_url.txt", "r") as f:
        urls = [url.strip() for url in f.readlines()]
    title = DIR+"autohome_data"+str(datetime.now().strftime("%m-%d-%H-%M"))+".json"
    
    pbar = tqdm(total=len(urls), desc="汽车之家进度")

    for url in urls:
        await process_url(url, title)
        pbar.update()

    pbar.close()
    print(f"数据已保存到 {title} 文件")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
