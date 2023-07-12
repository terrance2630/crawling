import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import concurrent.futures
import requests
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
table_name = 'dcd_data'
written_time = now.strftime('%Y_%m_%d')

# 创建新表
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    platform VARCHAR(255),
    views VARCHAR(255),
    shares VARCHAR(255),
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

TIMEOUT = 10
DIR = "dcd/"


def save_to_sql(result):
    # 在新表中插入数据
    insert_query = f"""
    INSERT INTO {table_name} (
        platform,
        views,
        shares,
        comments,
        likes,
        recommended,
        user_id,
        username,
        article_link,
        written_time
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        result['平台'],
        result['浏览数'],
        result['转发数'],
        result['回复数'],
        result['点赞数'],
        result['加精'],
        result['作者id'],
        result['作者'],
        result['文章'],
        written_time
    )
    cursor.execute(insert_query, values)

    # 提交事务
    cnx.commit()


# 将cookies和headers设置为全局变量
COOKIES = {
    'ttwid': '1%7CMRKDKFr-yjNzg6kuSYerbEL-z0rFvCRsCDUrwcW8OIg%7C1687757494%7Ceec0c5daf28c375dea832ed69de287c4b564df2cb071dcbb575c8d2afa3edb2c',
    'tt_webid': '7248863206289049143',
    'tt_web_version': 'new',
    'is_dev': 'false',
    'is_boe': 'false',
    'Hm_lvt_3e79ab9e4da287b5752d8048743b95e6': '1687757497',
    's_v_web_id': 'verify_ljcf8ob9_CsBS3COe_IfHR_4VXu_8gYr_EXFx3a5GmQSa',
    'city_name': '%E5%B9%BF%E5%B7%9E',
    'msToken': '3ZGuh51bgPauSSt1yMmX_gOdFIpM0F2KV8oAbAjuxz_6djI_P_-xh8GIrmDDFYAPXCmG6PCKCIbXUrciOJ-w2AvlNUd1hAmAamlt_dgBIds=',
    'Hm_lpvt_3e79ab9e4da287b5752d8048743b95e6': '1688351537',
    '_gid': 'GA1.2.737521777.1688351549',
    '_gat_gtag_UA_138671306_1': '1',
    '_ga_YB3EWSDTGF': 'GS1.1.1688351549.7.0.1688351549.60.0.0',
    '_ga': 'GA1.1.1729632978.1687757499',
}

HEADERS = {
    'authority': 'www.dongchedi.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    # 'cookie': 'ttwid=1%7CMRKDKFr-yjNzg6kuSYerbEL-z0rFvCRsCDUrwcW8OIg%7C1687757494%7Ceec0c5daf28c375dea832ed69de287c4b564df2cb071dcbb575c8d2afa3edb2c; tt_webid=7248863206289049143; tt_web_version=new; is_dev=false; is_boe=false; Hm_lvt_3e79ab9e4da287b5752d8048743b95e6=1687757497; s_v_web_id=verify_ljcf8ob9_CsBS3COe_IfHR_4VXu_8gYr_EXFx3a5GmQSa; city_name=%E5%B9%BF%E5%B7%9E; msToken=3ZGuh51bgPauSSt1yMmX_gOdFIpM0F2KV8oAbAjuxz_6djI_P_-xh8GIrmDDFYAPXCmG6PCKCIbXUrciOJ-w2AvlNUd1hAmAamlt_dgBIds=; Hm_lpvt_3e79ab9e4da287b5752d8048743b95e6=1688351537; _gid=GA1.2.737521777.1688351549; _gat_gtag_UA_138671306_1=1; _ga_YB3EWSDTGF=GS1.1.1688351549.7.0.1688351549.60.0.0; _ga=GA1.1.1729632978.1687757499',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

def get_dcd_page_source(url):
    try:
        response = requests.get(url, cookies=COOKIES, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except Exception as e:
        print(f"Exception occurred while navigating to {url}: {e}")
        return None
    return response.text

def scrape_dcd_dynamic_page(url):
    page_source = get_dcd_page_source(url)
    if not page_source:
        return None

    soup = BeautifulSoup(page_source, 'html.parser')
    json_data = soup.find('script', id='__NEXT_DATA__')
    if not json_data:
        print("未找到包含JSON数据的标签")
        return None

    try:
        data = json.loads(json_data.string)
    except json.JSONDecodeError:
        print("JSON解析失败")
        return None

    try:
        view_count = data['props']['pageProps']['articleData']['data']['read_count']
        share_count = data['props']['pageProps']['articleData']['data']['share_count']
        comment_count = data['props']['pageProps']['comment']['count']
        like_count = data['props']['pageProps']['articleData']['data']['digg_count']
        author_title = data['props']['pageProps']['articleData']['data']['motor_profile_info']['name']
        author_id = data['props']['pageProps']['articleData']['data']['motor_profile_info']['user_id']
        recommand = 'True' if data['props']['pageProps']['articleData']['data']['selected_tips'] else 'False'
    except KeyError as e:
        print(f"KeyError: {e} 在解析JSON数据时未找到")
        return None
    result = {
        "平台": "懂车帝",
        "浏览数": str(view_count),
        "转发数": str(share_count),
        "回复数": str(comment_count),
        "点赞数": str(like_count),
        "加精": str(recommand),
        "作者id": str(author_id),
        "作者": str(author_title),
        "文章": str(url)
    }
    return result


def extract_group_id(url):
    patterns = [r"group_id=(\d+)", r"/article/(\d+)"]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    print("URL解析失败:", url)
    return None

def scrape_and_save_dcd_urls(urls, filename):
    with tqdm(total=len(urls), desc="懂车帝平台进度") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(scrape_dcd_dynamic_page, f"https://www.dongchedi.com/ugc/article/{extract_group_id(url)}") for url in urls if extract_group_id(url) is not None]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    with open(filename, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(result, ensure_ascii=False) + "\n")
                pbar.update(1)

def process_urls(urls):
    title = DIR+"dcd_data"+str(datetime.now().strftime("%m-%d-%H-%M"))+".json"
    scrape_and_save_dcd_urls(urls, title)
    with open(title, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line.strip())
            save_to_sql(result)

if __name__ == "__main__":
    with open(DIR+"dcd_url.txt", 'r') as f:
        urls = [line.strip() for line in f]
    process_urls(urls)

