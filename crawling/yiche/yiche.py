import concurrent.futures
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime  
import json
import mysql.connector
import re

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
table_name = 'yiche_data'
written_time = now.strftime('%Y_%m_%d')


# 创建新表
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    platform VARCHAR(255),
    comments VARCHAR(255),
    likes VARCHAR(255),
    authorinfo TEXT,
    article_link TEXT,
    written_time VARCHAR(255)
)
"""
cursor.execute(create_table_query)

DIR = "yiche/"

firefox_options = Options()
#firefox_options.add_argument('--headless')
firefox_options.set_preference('permissions.default.image', 2)  # 禁止加载图片
firefox_options.set_preference('dom.webdriver.enabled', False)
firefox_options.set_preference('javascript.enabled', False)
firefox_options.set_preference('webdriver.load.strategy', 'unstable')
firefox_options.set_preference('browser.download.manager.showWhenStarting', False)


def save_to_sql(result):
    # 在新表中插入数据
    insert_query = f"""
    INSERT INTO {table_name} (
        platform,
        comments,
        likes,
        authorinfo,
        article_link,
        written_time
    ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        result['平台'],
        result['评论数'],
        result['点赞数'],
        json.dumps(result['作者列表'], ensure_ascii=False),
        result['文章'],
        written_time
    )
    cursor.execute(insert_query, values)
    # 提交事务
    cnx.commit()


def scrape_yiche_page_info(url):
    try:
        with webdriver.Firefox(options=firefox_options) as driver:
            driver.set_page_load_timeout(60)  # 设置超时限制
            driver.get(url)
            time.sleep(3)  # 延迟访问
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            comment_number = soup.find('li', class_='news-detail-position-pinglun').find('a').text.strip()
            like_number = soup.find('li', class_='news-detail-position-dianzan').find('a').text.strip()

            authors = soup.find_all('a', class_='news-detail-profile-active')
            author_list = []
            for author in authors:
                author_link = author['href']
                author_id = re.search(r'u(\d+)', author_link).group(1)

                author_list.append({
                    '作者名字': author.get_text(),
                    '作者ID': author_id,
                    '作者主页': author_link
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
    with open(DIR + title + ".json", 'r', encoding='utf-8') as f:
        for line in f.readlines():
            result = json.loads(line)
            save_to_sql(result)


def main():
    title = "yiche_data" + str(datetime.now().strftime("%m-%d-%H-%M"))

    # 从文件中读取url
    with open(DIR + 'yiche_url.txt', 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    # 抓取页面信息
    scrape_yiche_urls(urls, title)


if __name__ == "__main__":
    main()
