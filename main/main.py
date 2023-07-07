import asyncio
import json
import re
from tqdm import tqdm
from dcd_handler import scrape_dcd_urls
from autohome_handler import scrape_autohome_urls
from yiche_handler import scrape_yiche_urls
from xhs_handler import scrape_xhs_urls
from toutiao_handler import scrape_toutiao_urls
from datetime import datetime  
from concurrent.futures import TimeoutError

# 创建一个正则表达式字典来匹配每种URL
url_patterns = {
    "dcd": re.compile(r"(www\.)?dcdapp\.com|(api\.)?dcarapi\.com|(www\.)?dongchedi\.com"),
    "autohome": re.compile(r"(www\.)?autohome\.com\.cn"),
    "yiche": re.compile(r"(www\.)?yiche\.com"),
    "xhs": re.compile((r"(www\.)?xiaohongshu\.com")),
    "toutiao": re.compile(r"(www\.)?toutiao\.com")
}

async def process_url(url, title):
    for component, pattern in url_patterns.items():
        # 匹配 URL
        if pattern.search(url):
            # 使用 asyncio 的 wait_for 来设置超时，这样在特定时间内任务还未完成，就会抛出一个异常，我们可以捕获它并继续进行
            try:
                result = await loop.run_in_executor(None, globals()[f"scrape_{component}_urls"], [url])
                if result and result[0]:  # 确保结果不是空的
                    with open(title, 'a', encoding='utf-8') as f:
                        json.dump(result[0], f, ensure_ascii=False)
                        f.write('\n')
            except (Exception, TimeoutError):  # 捕获所有的异常包括超时异常
                print(f"Error occurred while processing url {url}")
            finally:
                return

async def main():
    # 从外部文件读取URLs
    with open("/Users/terrancew/Desktop/实习/main/urls.txt", "r") as f:
        urls = [url.strip() for url in f.readlines()]

    title = "/Users/terrancew/Desktop/实习/data/"+str(datetime.now().strftime("%m-%d-%H-%M"))+".json"
    
    pbar = tqdm(total=len(urls), desc="处理 URL 进度")

    for url in urls:
        await process_url(url, title)
        pbar.update()

    pbar.close()
    print(f"数据已保存到 {title} 文件")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
