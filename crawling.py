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

        with open(f'./qczj-data{str(count)}.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("HTML数据已保存到 data.html 文件")

    except Exception as e:
        print("爬取过程中出现错误:", e)

urls = [
    #"https://www.xiaohongshu.com/explore/64884937000000000800f53a?m_source=baidusem"
    "https://club.autohome.com.cn/bbs/thread-c-3495-105732139-1.html",
    "https://club.autohome.com.cn/bbs/thread-c-3495-105715932-1.html",
    "https://club.autohome.com.cn/bbs/thread-c-6960-105709282-1.html"
]




count = 0
for url in urls:
    scrape_dynamic_page(url, count)
    count+=1


