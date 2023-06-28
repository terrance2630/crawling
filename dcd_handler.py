import asyncio
import json
import re
from pyppeteer import launch
from pyppeteer.errors import NetworkError
from bs4 import BeautifulSoup
from tqdm import tqdm


async def get_dcd_page_source(url):
    browser = await launch()
    page = await browser.newPage()
    try:
        await page.goto(url, timeout=60000)  # Increase timeout to 60 seconds
        page_source = await page.content()
    except NetworkError as ne:
        print(f"NetworkError occurred while navigating to {url}: {ne}")
        page_source = None
    finally:
        await browser.close()
    return page_source


async def scrape_dcd_dynamic_page(url):
    try:
        page_source = await get_dcd_page_source(url)
        if page_source:
            soup = BeautifulSoup(page_source, 'html.parser')
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
                        "浏览量": view_count,
                        "转发量": share_count,
                        "回复量": comment_count,
                        "点赞量": like_count,
                        "加精": recommand,
                        "作者id": author_id,
                        "作者": author_title
                    }

                    return temp

                except json.JSONDecodeError:
                    print("JSON解析失败")
            else:
                print("未找到包含JSON数据的标签")
    except Exception as e:
        print("爬取过程中出现错误:", e)
    return None


def extract_group_id(url):
    pattern = r"group_id=(\d+)"
    match = re.search(pattern, url)
    if match:
        group_id = match.group(1)
        return group_id
    else:
        return None


async def scrape_dcd_urls(urls):
    tasks = []
    for url in urls:
        group_id = extract_group_id(url)
        if group_id is not None:
            base_url = "https://www.dongchedi.com/ugc/article/"
            new_url = base_url + group_id
            task = asyncio.create_task(scrape_dcd_dynamic_page(new_url))
            tasks.append(task)
        else:
            print("URL解析失败:", url)

    results = []
    with tqdm(total=len(tasks), desc="懂车帝平台进度") as pbar:
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            pbar.update(1)

    return results
