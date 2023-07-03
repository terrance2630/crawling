import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import concurrent.futures
import requests

cookies = {
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

headers = {
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
        response = requests.get(url, cookies=cookies, headers=headers)
    except Exception as e:
        print(f"Exception occurred while navigating to {url}: {e}")
        response = None
    return response

def scrape_dcd_dynamic_page(url):
    try:
        page_source = get_dcd_page_source(url)
        if page_source:
            soup = BeautifulSoup(page_source.text, 'html.parser')
            json_data = soup.find('script', id='__NEXT_DATA__')
            if json_data:
                json_content = json_data.string
                try:
                    data = json.loads(json_content)

                    view_count = data['props']['pageProps']['articleData']['data']['read_count']
                    share_count = data['props']['pageProps']['articleData']['data']['share_count']
                    comment_count = data['props']['pageProps']['comment']['count']
                    like_count = data['props']['pageProps']['articleData']['data']['digg_count']
                    author_title = data['props']['pageProps']['articleData']['data']['motor_profile_info']['name']
                    author_id = data['props']['pageProps']['articleData']['data']['motor_profile_info']['user_id']
                    if data['props']['pageProps']['articleData']['data']['selected_tips']:
                        recommand = 'True'
                    else:
                        recommand = 'False'

                    temp = {
                        "平台": "懂车帝",
                        "浏览量": str(view_count),
                        "转发量": str(share_count),
                        "回复量": str(comment_count),
                        "点赞量": str(like_count),
                        "加精": str(recommand),
                        "作者id": str(author_id),
                        "作者": str(author_title),
                        "文章": str(url)
                    }

                    return temp

                except json.JSONDecodeError:
                    print("JSON解析失败")
            else:
                print("未找到包含JSON数据的标签")
    except Exception as e:
        print("懂车帝爬取过程中出现错误:", e)
    return None

def extract_group_id(url):
    pattern = r"group_id=(\d+)"
    match = re.search(pattern, url)
    if match:
        group_id = match.group(1)
        return group_id
    else:
        return None

def scrape_dcd_urls(urls):
    tasks = []
    for url in urls:
        group_id = extract_group_id(url)
        if group_id is not None:
            base_url = "https://www.dongchedi.com/ugc/article/"
            new_url = base_url + group_id
            task = (scrape_dcd_dynamic_page, new_url)  # 将函数和参数一起保存为元组
            tasks.append(task)
        else:
            print("URL解析失败:", url)

    results = []
    with tqdm(total=len(tasks), desc="懂车帝平台进度") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(func, arg) for func, arg in tasks]  # 在此处分别提取函数和参数
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    results.append(result)
                pbar.update(1)

    return results








