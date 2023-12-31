import asyncio
import json
import re
from pyppeteer import launch
from pyppeteer.errors import NetworkError
from bs4 import BeautifulSoup
import aiofiles


async def get_page_source(url):
    browser = await launch()
    page = await browser.newPage()
    try:
        await page.goto(url, timeout=60000)  # 增加超时时间为60秒
        page_source = await page.content()
    except NetworkError as ne:
        print(f"访问 {url} 时发生 NetworkError 错误: {ne}")
        page_source = None
    finally:
        await browser.close()
    return page_source


async def scrape_dynamic_page(url, count):
    try:
        page_source = await get_page_source(url)
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

                    temp = {
                        "平台": "懂车帝",
                        "浏览量": view_count,
                        "转发量": share_count,
                        "回复量": comment_count,
                        "点赞量": like_count,
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


async def process_single_url(url):
    group_id = extract_group_id(url)
    if group_id is not None:
        base_url = "https://www.dongchedi.com/ugc/article/"
        new_url = base_url + group_id
        result = await scrape_dynamic_page(new_url, 0)
        if result is not None:
            return result
    else:
        print("URL解析失败:", url)
    return None


async def process_multiple_urls(urls):
    tasks = []
    for i, url in enumerate(urls):
        task = asyncio.create_task(process_single_url(url))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    filtered_results = [result for result in results if result is not None]

    async with aiofiles.open('data.json', 'a', encoding='utf-8') as f:
        await f.write(json.dumps(filtered_results, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    urls = [
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769659585436680&share_token=d43a5fed-7092-4692-8db5-8f2d2773f491",
        "https://api.dcarapi.com/motor/feoffline/ugcs/article.html?link_source=share&group_id=7248523462866665984&share_token=58717795-0c7a-4b2e-ba40-70b35a18405a",
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769655459094621"
        # 添加其他 URL
    ]

    asyncio.run(process_multiple_urls(urls))
