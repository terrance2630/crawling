import asyncio
import json
import re
from tqdm import tqdm
from dcd_handler import scrape_dcd_urls
from autohome_handler import scrape_autohome_urls
from yiche_handler import scrape_yiche_urls
from xhs_handler import process_urls
from toutiao_handler import scrape_toutiao_urls  # 引入头条爬取函数

dcd_pattern = re.compile(r"(www\.)?dcdapp\.com|(api\.)?dcarapi\.com")
autohome_pattern = re.compile(r"(www\.)?autohome\.com\.cn")
yiche_pattern = re.compile(r"(www\.)?yiche\.com")
xhs_pattern = re.compile((r"(www\.)?xiaohongshu\.com"))
toutiao_pattern = re.compile(r"(www\.)?toutiao\.com")  # 定义头条的正则表达式

def analyze_url(url):
    if dcd_pattern.search(url):
        return "dcd"
    elif autohome_pattern.search(url):
        return "autohome"
    elif yiche_pattern.search(url):
        return "yiche"
    elif xhs_pattern.search(url):
        return "xhs"
    elif toutiao_pattern.search(url):  # 添加头条的匹配
        return "toutiao"
    else:
        return None

async def process_batch(urls):
    dcd_urls = []
    autohome_urls = []
    yiche_urls = []
    xhs_urls = []
    toutiao_urls = []  # 定义头条 URL 列表

    for url in urls:
        component = analyze_url(url)
        if component == "dcd":
            dcd_urls.append(url)
        elif component == "autohome":
            autohome_urls.append(url)
        elif component == "yiche":
            yiche_urls.append(url)
        elif component == "xhs":
            xhs_urls.append(url)
        elif component == "toutiao":  # 添加头条 URL
            toutiao_urls.append(url)

    loop = asyncio.get_event_loop()

    dcd_task = scrape_dcd_urls(dcd_urls)
    autohome_task = loop.run_in_executor(None, scrape_autohome_urls, autohome_urls)
    yiche_task = loop.run_in_executor(None, scrape_yiche_urls, yiche_urls)
    xhs_task = loop.run_in_executor(None, process_urls, xhs_urls)
    toutiao_task = loop.run_in_executor(None, scrape_toutiao_urls, toutiao_urls)  # 添加头条爬取任务

    dcd_results = await dcd_task
    autohome_results = await autohome_task
    yiche_results = await yiche_task
    xhs_results = await xhs_task
    toutiao_results = await toutiao_task  # 等待头条爬取任务完成

    all_results = dcd_results + autohome_results + yiche_results + xhs_results + toutiao_results  # 将头条爬取结果加入总结果

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
        "https://news.yiche.com/xinchexiaoxi/20230521/0081822289.html",
        'https://news.yiche.com/xinchexiaoxi/20230521/0081822289.html',
        "https://www.xiaohongshu.com/explore/64884937000000000800f53a?m_source=baidusem",
        "https://www.xiaohongshu.com/explore/641c2d2b0000000013002ad8?m_source=baidusem",
        "https://www.xiaohongshu.com/explore/644b96b3000000000800cd18?m_source=baidusem",
        # 添加头条的 URL
        "https://www.toutiao.com/article/7235891710436459063/?channel=&source=search_tab",
        "https://www.toutiao.com/article/7249150127242363447/?channel=&source=search_tab",
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
