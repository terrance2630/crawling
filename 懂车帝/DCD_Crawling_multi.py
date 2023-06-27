import asyncio
import json
import re
from pyppeteer import launch
from bs4 import BeautifulSoup

async def get_page_source(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    page_source = await page.content()
    await browser.close()
    return page_source

async def scrape_dynamic_page(url, count):
    try:
        page_source = await get_page_source(url)
        soup = BeautifulSoup(page_source, 'html.parser')
        json_data = soup.find('script', id='__NEXT_DATA__')
        if json_data:
            json_content = json_data.string
            try:
                data = json.loads(json_content)
                with open(f'./data{str(count)}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"JSON数据已保存到 data{str(count)}.json 文件")
            except json.JSONDecodeError:
                print("JSON解析失败")
        else:
            print("未找到包含JSON数据的标签")
    except Exception as e:
        print("爬取过程中出现错误:", e)

def extract_group_id(url):
    pattern = r"group_id=(\d+)"
    match = re.search(pattern, url)
    if match:
        group_id = match.group(1)
        return group_id
    else:
        return None

async def main():
    base_url = "https://www.dongchedi.com/ugc/article/"
    urls = [
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769659585436680&share_token=d43a5fed-7092-4692-8db5-8f2d2773f491",
        "https://api.dcarapi.com/motor/feoffline/ugcs/article.html?link_source=share&group_id=7248523462866665984&share_token=58717795-0c7a-4b2e-ba40-70b35a18405a",
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769655459094621"
        # 添加其他 url
    ]

    new_urls = []
    for url in urls:
        group_id = extract_group_id(url)
        new_url = base_url + group_id
        new_urls.append(new_url)

    tasks = []
    for i, url in enumerate(new_urls):
        task = scrape_dynamic_page(url, i)
        tasks.append(task)

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
