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
import mysql.connector

try:
    cnx = mysql.connector.connect(
        host='localhost',
        user='root',
        password='dasheng202307',
        database='crawling_data'
    )
except mysql.connector.Error as err:
    if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
        # 如果数据库不存在，创建新的数据库
        cnx = mysql.connector.connect(
            host='localhost',
            user='root',
            password='dasheng202307',
        )
        cursor = cnx.cursor()
        cursor.execute("CREATE DATABASE crawling_data")
        cnx.database = 'crawling_data'
    else:
        raise

cursor = cnx.cursor()

now = datetime.now()
table_name = 'autohome_data'
written_time = now.strftime('%Y_%m_%d')

# 创建新表
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    platform VARCHAR(255),
    views VARCHAR(255),
    comments VARCHAR(255),
    likes VARCHAR(255),
    recommended VARCHAR(255),
    user_id VARCHAR(5000),
    username VARCHAR(5000),
    article_link TEXT,
    written_time VARCHAR(255)
)
"""
cursor.execute(create_table_query)

DIR = "autohome/"

# 创建正则表达式对象
autohome_pattern = re.compile(r"(www\.)?autohome\.com\.cn")
firefox_options = Options()
firefox_options.set_preference('permissions.default.image', 2)  # 禁止加载图片

def get_text(element):
    return element.text.strip() if element and element.text.strip() else '0'

def save_to_sql(result):
    # 在新表中插入数据
    insert_query = f"""
    INSERT INTO {table_name} (
        platform,
        views,
        comments,
        likes,
        recommended,
        user_id,
        username,
        article_link,
        written_time
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        result['平台'],
        result['浏览数'],
        result['评论数'],
        result['点赞数'],
        result['加精推荐'],
        result['用户id'],
        result['用户名'],
        result['文章'],
        written_time
    )
    cursor.execute(insert_query, values)
    # 提交事务
    cnx.commit()


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

    with open(title, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line.strip())
            save_to_sql(result)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
