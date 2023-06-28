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

def scrape_dynamic_page(url, count):
    try:
        page_source = asyncio.get_event_loop().run_until_complete(get_page_source(url))
        soup = BeautifulSoup(page_source, 'html.parser')
        with open(f'./data{str(count)}.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("源代码已保存")
           
    except Exception as e:
        print("爬取过程中出现错误:", e)

    
url = 'https://www.toutiao.com/article/7235891710436459063/?channel=&source=search_tab'

scrape_dynamic_page(url, 0)

