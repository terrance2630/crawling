import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

# 设置请求头和cookies
def setup_request():
    cookie = {'timestamp2': '1688092677969'}
    header = {
        'authority': 'mcs.zijieapi.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
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
        'user-agent':  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    return header, cookie

# 获取网页内容
def get_page(link, header, cookie):
    try:
        page = requests.get(link, headers=header, cookies=cookie)
        return BeautifulSoup(page.text, "html.parser")
    except Exception as e:
        print(f"获取页面出错，错误信息：{str(e)}")
        return None

# 从页面内容中提取作者信息
def get_author_info(soup):
    try:
        script_tag = soup.find('script', type='application/ld+json')
        json_str = script_tag.string.strip()
        name = re.search(r'"author":\s*{\s*"@type":\s*"Person",\s*"name":\s*"([^"]+)"', json_str).group(1)
        url = re.search(r'"url":\s*"([^"]+)"', json_str).group(1)
        parsed_url = urlparse(url)
        path = parsed_url.path
        user_id = path.split("/")[-1]
        return {"作者": name, "作者ID": user_id, "作者主页": url}
    except Exception as e:
        print(f"获取作者信息出错，错误信息：{str(e)}")
        return None

# 从页面内容中提取互动数据
def get_interaction_data(soup):
    try:
        script_tag = soup.findAll('script')
        for script in script_tag:
            script_text = script.text.strip()
            match = re.search(r'window\.__INITIAL_SSR_STATE__\s*=\s*({.*?})', script_text)
            if match:
                data_json = match.group(1)
                break

        likes_match = re.search(r'"likes"\s*:\s*"([^"]+)"', data_json)
        collects_match = re.search(r'"collects"\s*:\s*(\d+)', data_json)
        share_count_match = re.search(r'"shareCount"\s*:\s*(\d+)', data_json)
        comments_match = re.search(r'"comments"\s*:\s*(\d+)', data_json)
        
        likes = likes_match.group(1) if likes_match else None
        collects = collects_match.group(1) if collects_match else None
        share_count = share_count_match.group(1) if share_count_match else None
        comments = comments_match.group(1) if comments_match else None

        return {"点赞数": likes, "收藏数": collects, "分享数": share_count, "评论数": comments}
    except Exception as e:
        print(f"获取互动数据出错，错误信息：{str(e)}")
        return None

# 更新主函数，让其接受 url 作为参数
def main(url, header, cookie):
    soup = get_page(url, header, cookie)
    if soup:
        author_info = get_author_info(soup)
        interaction_data = get_interaction_data(soup)
        return {"平台":"小红书", **interaction_data, **author_info}

def process_urls(urls, max_workers=10):
    header, cookie = setup_request()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(main, url, header, cookie) for url in urls]
        return [future.result() for future in futures]

# 测试代码
urls = [
    "https://www.xiaohongshu.com/explore/64884937000000000800f53a?m_source=baidusem",
    "https://www.xiaohongshu.com/explore/641c2d2b0000000013002ad8?m_source=baidusem",
    "https://www.xiaohongshu.com/explore/644b96b3000000000800cd18?m_source=baidusem",
]
print(process_urls(urls))
