import requests
from bs4 import BeautifulSoup
import concurrent.futures
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from datetime import datetime  
import json
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
table_name = 'xhs_data'
written_time = now.strftime('%Y_%m_%d')

# 创建新表
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    platform VARCHAR(255),
    likes VARCHAR(255),
    collects VARCHAR(255),
    shares VARCHAR(255),
    comments VARCHAR(255),
    article_link TEXT,
    username VARCHAR(5000),
    user_id VARCHAR(5000),
    user_link TEXT,
    written_time VARCHAR(255)
)
"""
cursor.execute(create_table_query)
DIR = "xhs/"
TIMEOUT = 10

def save_to_sql(result):
    # 在新表中插入数据
    insert_query = f"""
    INSERT INTO {table_name} (
        platform,
        likes,
        collects,
        shares,
        comments,
        article_link,
        username,
        user_id,
        user_link,
        written_time
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """ 
    values = (
        result['平台'],
        result['点赞数'],
        result['收藏数'],
        result['分享数'],
        result['评论数'],
        result['文章'],
        result['作者'],
        result['作者ID'],
        result['作者主页'],
        written_time
    )
    
    cursor.execute(insert_query, values)
    cnx.commit()

# 设置请求头和cookies
def setup_request():
    cookie = {'timestamp2': '1688092677969'}
    header = {
        'authority': 'www.xiaohongshu.com',
        'accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, image/avif, image/webp, image/apng,*/*;q=0.8, application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-TW, zh; q=0.9, en-US; q=0.8, en; q=0.7, zh-CN; q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not?A_Brand";v="g", "Chromium"; v="108", "Google Chrome"; v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent':  'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36'
    }
    return header, cookie

# 获取网页内容
def get_page(link, header, cookie):
    try:
        page = requests.get(link, headers=header, cookies=cookie)
        return BeautifulSoup(page.text, "html.parser")
    except Exception as e:
        print(f"小红书获取页面出错，错误信息：{str(e)}")
        return None

# 从页面内容中提取作者信息
def get_author_info(soup):
    try:
        script_tag = soup.find('script', type='application/ld+json')
        author_info = script_tag.string.strip()
        name = re.search(r'"author":\s*{\s*"@type":\s*"Person",\s*"name":\s*"([^"]+)"', author_info).group(1)
        url = re.search(r'"url":\s*"([^"]+)"', author_info).group(1)
        parsed_url = urlparse(url)
        path = parsed_url.path
        user_id = path.split("/")[-1]
        return {"作者": name, "作者ID": user_id, "作者主页": url}
    except Exception as e:
        print(f"获取作者信息出错，错误信息：{str(e)}")
        return None

# 从页面内容中提取互动数据
def get_interaction_data(soup, url):
    try:
        script_tag = soup.findAll('script')
        for script in script_tag:
            script_text = script.text.strip()
            match = re.search(r'window\.__INITIAL_SSR_STATE__\s*=\s*({.*?})', script_text)
            if match:
                interaction_data = match.group(1)
                break

        likes_match = re.search(r'"likes"\s*:\s*"([^"]+)"', interaction_data)
        collects_match = re.search(r'"collects"\s*:\s*(\d+)', interaction_data)
        share_count_match = re.search(r'"shareCount"\s*:\s*(\d+)', interaction_data)
        comments_match = re.search(r'"comments"\s*:\s*(\d+)', interaction_data)
        
        likes = likes_match.group(1) if likes_match else '0'
        collects = collects_match.group(1) if collects_match else '0'
        share_count = share_count_match.group(1) if share_count_match else '0'
        comments = comments_match.group(1) if comments_match else '0'

        return {
            "点赞数": likes,
            "收藏数": collects,
            "分享数": share_count,
            "评论数": comments,
            "文章": str(url)
            }
    except Exception as e:
        print(f"获取互动数据出错，错误信息：{str(e)}")
        return None

# 更新主函数，让其接受 url 作为参数
def main(url, header, cookie):
    soup = get_page(url, header, cookie)
    if soup:
        author_info = get_author_info(soup)
        interaction_data = get_interaction_data(soup, url)
        return {"平台":"小红书", **interaction_data, **author_info}


def scrape_xhs_urls(urls):
    header, cookie = setup_request()

    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(main, url, header, cookie) for url in urls]

        with tqdm(total=len(futures), desc="小红书进度") as pbar:
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
                pbar.update(1)
    
    return results
def process_urls(urls):
    title = "xhs_data" + str(datetime.now().strftime("%m-%d-%H-%M"))
    header, cookie = setup_request()

    with ThreadPoolExecutor(max_workers=50) as executor:
        with tqdm(total=len(urls), desc="小红书进度") as pbar:
            for url in urls:
                result = main(url, header, cookie)
                if result:
                    with open(DIR + title + ".json", 'a', encoding='utf-8') as f:
                        f.write(json.dumps(result, ensure_ascii=False))
                        f.write("\n")  # Add a newline to separate each entry
                pbar.update(1)

    with open(DIR + title + ".json", 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line.strip())
            save_to_sql(result)

if __name__ == "__main__":
    with open(DIR + "xhs_url.txt", 'r') as f:
        urls = [line.strip() for line in f]
    process_urls(urls)

