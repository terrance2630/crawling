import concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm

import requests

cookies = {
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
    'msToken': 'cmrRgpCP-jsIvMo3SqJfSH8LRNrpoY1vt-za6QTTcZUfIbzW3mmRCgnUViWJPwNSZmluT4EynsRcUuh5leeoR73pJ9SIgjnEghbwEY9m7Vc=',
    '_ga_QEHZPBE5HH': 'GS1.1.1688116265.8.1.1688118100.0.0.0',
    'ttwid': '1%7C1iX7OSSDI7Lz9zV8CnApEsq_Y4FTzBlH8MjAVsz9XEc%7C1688118101%7C101b5537e40581b0ccd8b2bbe295de74d9f90e34d76ef2292ac0121da3f796e5',
    'tt_scid': 'K05thr5cM0Qgt8.qrLU6xYahmzOCt769EcXwKJauZx4kclGyh0DKLNQqXhjOntHq0094',
}

headers = {
    'authority': 'www.toutiao.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    # 'cookie': 'passport_csrf_token=02b7b12965b97a09b9c4b399cc73126c; tt_webid=7248933611839604282; ttcid=23c752c151834b4c9518247705eaee1475; local_city_cache=%E5%8C%97%E4%BA%AC; csrftoken=4de5ffec509f0897bec2a8c7405a6906; _ga=GA1.1.682536941.1687773904; s_v_web_id=verify_ljcp077a_5gVj3l2X_w2vI_4CQ7_9MIs_whHLJoETFebr; _S_WIN_WH=1470_809; _S_DPR=2; _S_IPAD=0; msToken=cmrRgpCP-jsIvMo3SqJfSH8LRNrpoY1vt-za6QTTcZUfIbzW3mmRCgnUViWJPwNSZmluT4EynsRcUuh5leeoR73pJ9SIgjnEghbwEY9m7Vc=; _ga_QEHZPBE5HH=GS1.1.1688116265.8.1.1688118100.0.0.0; ttwid=1%7C1iX7OSSDI7Lz9zV8CnApEsq_Y4FTzBlH8MjAVsz9XEc%7C1688118101%7C101b5537e40581b0ccd8b2bbe295de74d9f90e34d76ef2292ac0121da3f796e5; tt_scid=K05thr5cM0Qgt8.qrLU6xYahmzOCt769EcXwKJauZx4kclGyh0DKLNQqXhjOntHq0094',
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

def scrape_toutiao_page_info(url):
    

    try:
        response = requests.get(url, params=params, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到并打印点赞数量
        like_count_div = soup.find('div', class_='digg-icon')
        like_count = like_count_div.find_next_sibling('span').text

        # 找到并打印评论数量
        comment_count_div = soup.find('div', class_='detail-interaction-comment')
        comment_count = comment_count_div.find('span').text

        # 找到并打印用户主页和用户名
        user_meta_div = soup.find('div', class_='article-meta')
        user_name_span = user_meta_div.find('span', class_='name')
        user_homepage = 'www.toutiao.com/'+user_name_span.find('a')['href']
        user_name = user_name_span.text.strip()

        result = {
            '平台': "头条",
            '评论数': comment_count,
            '点赞数': like_count,
            '用户名': user_name,
            '用户主页': user_homepage,
            "文章": url
        }

        return result

    except Exception as e:
        print("头条在爬取过程中出现错误:", e)
        return None


def scrape_toutiao_urls(urls):
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_toutiao_page_info, url) for url in urls]

        with tqdm(total=len(futures), desc="头条进度") as pbar:
            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())
                pbar.update(1)

    return result
