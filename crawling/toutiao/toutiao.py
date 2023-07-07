import concurrent.futures
from bs4 import BeautifulSoup
import json
import re
import requests
from datetime import datetime  
from tqdm import tqdm

DIR = "toutiao/"
TIMEOUT = 10
URL_PATTERN = re.compile(r"(www\.)?toutiao\.com")

def get_user_info(topic_id):
    try:
        headers = {
            'authority': 'www.toutiao.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 'cookie': 'passport_csrf_token=02b7b12965b97a09b9c4b399cc73126c; tt_webid=7248933611839604282; ttcid=23c752c151834b4c9518247705eaee1475; local_city_cache=%E5%8C%97%E4%BA%AC; csrftoken=4de5ffec509f0897bec2a8c7405a6906; _ga=GA1.1.682536941.1687773904; s_v_web_id=verify_ljcp077a_5gVj3l2X_w2vI_4CQ7_9MIs_whHLJoETFebr; _S_WIN_WH=1470_809; _S_DPR=2; _S_IPAD=0; tt_scid=SCkf8Rx36nrIti7eFR5OvFbiKyek.bzEbjyeYoWL39Tr4HwfX1Y-rqzoq0pcIofj9efb; ttwid=1%7C1iX7OSSDI7Lz9zV8CnApEsq_Y4FTzBlH8MjAVsz9XEc%7C1688528473%7Cfd436e7d0a1c872f2505ed6a0dcdddc999c1e1652230204d7dd9a8916849453e; msToken=83BTAa7bRjC7ZdEPvKBKoLFnY6aG4xHW4bsMs1Xyls7-NY8j7tpn5gztBlkIVDI7mDnSr9tNWFjSr_JHzjH0Bboqia90D_21kSql_eXs7Ck=; _ga_QEHZPBE5HH=GS1.1.1688528464.15.0.1688528475.0.0.0',
            'referer': f'https://www.toutiao.com/article/{topic_id}/?channel=&source=search_tab',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        params = {
            'aid': '24',
            'app_name': 'toutiao_web',
            'offset': '0',
            'count': '20',
            'group_id': topic_id,
            'item_id': topic_id,
            '_signature': '_02B4Z6wo00f01bReIKAAAIDBLDW30aQZDwW0eiQAAAm0ySJtiPGiSdZb20ehCinMYwQoQfLAAFgoRmOVbHyoccOwc..75ICL3KIezNIEMjWCebI.lnN8C6SD0H45DbAa57TvU5ODl7aLmqLD25',
        }
        response = requests.get('https://www.toutiao.com/article/v2/tab_comments/', params=params, headers=headers)
        data = json.loads(response.text)
        user_name = data['group']['user_name']
        user_id = data['group']['user_id']
        comment = data['total_number']
        return (str(comment), str(user_id), str(user_name))
    except Exception as e:
        print(f"Error in get_user_info: {e}")
        return (None, None, None)

def get_like_count(topic_id):
    try:
        cookies = {
            'tt_search_log': 'eyJxdWVyeV9pbnB1dF90aW1lIjoxMTIyLCJzZWFyY2hfcHJlc3NfZHVyYXRpb24iOjkxLCJzZWFyY2hfdmlld3BvcnRfeCI6LTEsInNlYXJjaF92aWV3cG9ydF95IjotMX0=',
            'passport_csrf_token': '02b7b12965b97a09b9c4b399cc73126c',
            'tt_webid': '7248933611839604282',
            'ttcid': '23c752c151834b4c9518247705eaee1475',
            'local_city_cache': '%E5%8C%97%E4%BA%AC',
            'csrftoken': '4de5ffec509f0897bec2a8c7405a6906',
            '_ga': 'GA1.1.682536941.1687773904',
            's_v_web_id': 'verify_ljcp077a_5gVj3l2X_w2vI_4CQ7_9MIs_whHLJoETFebr',
            '_S_WIN_WH': '1470_809',
            '_S_DPR': '2',
            '_S_IPAD': '0',
            'msToken': 'nPj_OKNvauecFtuoyHJjvl31nY6_ogWdgfHaGP4R2I108hmZUWcizhH4euV2kB9Z4FC8GXNaTOiKUBLZ9cIUiHFiI1js5a16uTMMAfiRXRQ=',
            '_ga_QEHZPBE5HH': 'GS1.1.1688528464.15.1.1688528667.0.0.0',
            'ttwid': '1%7C1iX7OSSDI7Lz9zV8CnApEsq_Y4FTzBlH8MjAVsz9XEc%7C1688528669%7Cc73558de93bdd2505fdf1b9b0201c69440e045e3191ec1efe1213b711ba7119f',
            'tt_scid': 'DMXN71QYr801tXEzFcPQei7k2rk0DlbUKzsg6jn6xgYBdMlrxZmOZXXHARF0D1-p3596',
        }
        headers = {
            'authority': 'www.toutiao.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            # 'cookie': 'tt_search_log=eyJxdWVyeV9pbnB1dF90aW1lIjoxMTIyLCJzZWFyY2hfcHJlc3NfZHVyYXRpb24iOjkxLCJzZWFyY2hfdmlld3BvcnRfeCI6LTEsInNlYXJjaF92aWV3cG9ydF95IjotMX0=; passport_csrf_token=02b7b12965b97a09b9c4b399cc73126c; tt_webid=7248933611839604282; ttcid=23c752c151834b4c9518247705eaee1475; local_city_cache=%E5%8C%97%E4%BA%AC; csrftoken=4de5ffec509f0897bec2a8c7405a6906; _ga=GA1.1.682536941.1687773904; s_v_web_id=verify_ljcp077a_5gVj3l2X_w2vI_4CQ7_9MIs_whHLJoETFebr; _S_WIN_WH=1470_809; _S_DPR=2; _S_IPAD=0; msToken=nPj_OKNvauecFtuoyHJjvl31nY6_ogWdgfHaGP4R2I108hmZUWcizhH4euV2kB9Z4FC8GXNaTOiKUBLZ9cIUiHFiI1js5a16uTMMAfiRXRQ=; _ga_QEHZPBE5HH=GS1.1.1688528464.15.1.1688528667.0.0.0; ttwid=1%7C1iX7OSSDI7Lz9zV8CnApEsq_Y4FTzBlH8MjAVsz9XEc%7C1688528669%7Cc73558de93bdd2505fdf1b9b0201c69440e045e3191ec1efe1213b711ba7119f; tt_scid=DMXN71QYr801tXEzFcPQei7k2rk0DlbUKzsg6jn6xgYBdMlrxZmOZXXHARF0D1-p3596',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        params = {
            'channel': '',
            'source': 'search_tab',
        }
        response = requests.get(f'https://www.toutiao.com/article/{topic_id}/', params=params, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        praise_span = soup.select_one('.detail-like span')
        if praise_span:
            praise_count = (praise_span.text)
            praise_count = "0" if praise_count == "赞" else praise_count
            return praise_count
        else:
            print("未找到赞的数量")
            return '-1'
    except Exception as e:
        print(f"Error in get_like_count: {e}")
        return '-1'


def scrape_toutiao_urls(urls):
    result = []
    with tqdm(total=len(urls), desc="头条平台进度") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(scrape_toutiao_page_info, url) for url in urls]

            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res is not None:
                    result.append(res)
                pbar.update(1)
    return result

def scrape_toutiao_page_info(url, title):
    match = re.search(r'/article/(\d+)/', url)
    if match:
        topic_id = match.group(1)
    else:
        return None

    comment_count, user_id, user_name = get_user_info(topic_id)
    like_count = get_like_count(topic_id)

    if comment_count is None or user_id is None or user_name is None or like_count == '-1':
        print(f"Error while scraping url: {url}")
        return None

    result = {
        '平台': "头条",
        '评论数': comment_count,
        '点赞数': like_count,
        '用户名': user_name,
        '用户id': user_id,
        "文章": url
    }

    with open(DIR+title+".json", 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False))
        f.write("\n")  # Add a newline to separate each entry

def process_urls(urls):
    title = "toutiao_data" + str(datetime.now().strftime("%m-%d-%H-%M"))
    with tqdm(total=len(urls), desc="头条平台进度") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(scrape_toutiao_page_info, url, title) for url in urls]

            for future in concurrent.futures.as_completed(futures):
                pbar.update(1)

if __name__ == "__main__":
    with open(DIR+"toutiao_url.txt", 'r') as f:
        urls = [line.strip() for line in f]
    process_urls(urls)


