import asyncio
import json
from tqdm import tqdm
from dcd_handler import scrape_dcd_urls
from autohome_handler import scrape_autohome_urls
from yiche_handler import scrape_yiche_urls

async def main():
    dcd_urls = [
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769659585436680&share_token=d43a5fed-7092-4692-8db5-8f2d2773f491",
        "https://api.dcarapi.com/motor/feoffline/ugcs/article.html?link_source=share&group_id=7248523462866665984&share_token=58717795-0c7a-4b2e-ba40-70b35a18405a",
        "https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=1769655459094621"
        # 添加其他懂车帝平台的 URL
    ]

    autohome_urls = [
        'https://club.autohome.com.cn/bbs/thread-c-3495-105732139-1.html',
        'https://club.autohome.com.cn/bbs/thread-c-3495-105715932-1.html',
        'https://club.autohome.com.cn/bbs/thread-c-6960-105709282-1.html'
        # 添加其他汽车之家平台的 URL
    ]

    yiche_urls = [
        'https://news.yiche.com/xinchexiaoxi/20230521/0081822289.html'
        # 添加其他易车平台的 URL
    ]

    loop = asyncio.get_event_loop()

    dcd_task = scrape_dcd_urls(dcd_urls)
    autohome_task = loop.run_in_executor(None, scrape_autohome_urls, autohome_urls)
    yiche_task = loop.run_in_executor(None, scrape_yiche_urls, yiche_urls)

    dcd_results = await dcd_task
    autohome_results = await autohome_task
    yiche_results = await yiche_task

    all_results = dcd_results + autohome_results + yiche_results

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
        print("数据已保存到 data.json 文件")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
