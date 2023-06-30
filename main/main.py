import asyncio
import json
import re
from tqdm import tqdm
from dcd_handler import scrape_dcd_urls
from autohome_handler import scrape_autohome_urls
from yiche_handler import scrape_yiche_urls

dcd_pattern = re.compile(r"(www\.)?dcdapp\.com|(api\.)?dcarapi\.com")
autohome_pattern = re.compile(r"(www\.)?autohome\.com\.cn")
yiche_pattern = re.compile(r"(www\.)?yiche\.com")

def analyze_url(url):
    if dcd_pattern.search(url):
        return "dcd"
    elif autohome_pattern.search(url):
        return "autohome"
    elif yiche_pattern.search(url):
        return "yiche"
    else:
        return None

async def process_batch(urls):
    dcd_urls = []
    autohome_urls = []
    yiche_urls = []

    for url in urls:
        component = analyze_url(url)
        if component == "dcd":
            dcd_urls.append(url)
        elif component == "autohome":
            autohome_urls.append(url)
        elif component == "yiche":
            yiche_urls.append(url)

# 处理 dcd_urls、autohome_urls 和 yiche_urls

    loop = asyncio.get_event_loop()

    dcd_task = scrape_dcd_urls(dcd_urls)
    autohome_task = loop.run_in_executor(None, scrape_autohome_urls, autohome_urls)
    yiche_task = loop.run_in_executor(None, scrape_yiche_urls, yiche_urls)

    dcd_results = await dcd_task
    autohome_results = await autohome_task
    yiche_results = await yiche_task

    all_results = dcd_results + autohome_results + yiche_results

    with open('data.json', 'a', encoding='utf-8') as f:
        for result in all_results:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')

async def main():
    urls = [
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769659585436680&share_token=d43a5fed-7092-4692-8db5-8f2d2773f491",
        "https://api.dcarapi.com/motor/feoffline/ugcs/article.html?link_source=share&group_id=7248523462866665984&share_token=58717795-0c7a-4b2e-ba40-70b35a18405a",
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769655459094621",
        "https://club.autohome.com.cn/bbs/thread-c-3495-105732139-1.html",
        "https://club.autohome.com.cn/bbs/thread-c-3495-105715932-1.html",
        "https://club.autohome.com.cn/bbs/thread-c-6960-105709282-1.html",
        "https://news.yiche.com/xinchexiaoxi/20230521/0081822289.html"
        # 添加其他网址
    ]

    batch_size = 10  # 每个批次处理的 URL 数量
    num_batches = len(urls) // batch_size + (len(urls) % batch_size > 0)

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = start_index + batch_size
        batch_urls = urls[start_index:end_index]
        await process_batch(batch_urls)

    print("数据已保存到 data.json 文件")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
