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

# 创建一个正则表达式字典来匹配每种URL
url_patterns = {
    "dcd": re.compile(r"(www\.)?dcdapp\.com|(api\.)?dcarapi\.com|(www\.)?dongchedi\.com"),
    "autohome": re.compile(r"(www\.)?autohome\.com\.cn"),
    "yiche": re.compile(r"(www\.)?yiche\.com"),
    "xhs": re.compile((r"(www\.)?xiaohongshu\.com")),
    "toutiao": re.compile(r"(www\.)?toutiao\.com")
}

async def process_batch(urls, title):
    tasks = {}
    results = []

    for component, pattern in url_patterns.items():
        # 创建一个URL列表，匹配给定的组件模式
        component_urls = [url for url in urls if pattern.search(url)]
        if component_urls:
            # 为每个组件创建一个任务，并将其存储在字典中
            task = loop.run_in_executor(None, globals()[f"scrape_{component}_urls"], component_urls)
            tasks[component] = task

    # 等待所有任务完成，并收集结果
    for component, task in tasks.items():
        result = await task
        results += result

    # 将结果写入文件
    with open(title, 'a', encoding='utf-8') as f:
        for result in results:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')

    # 返回处理的 URL 数量
    return len(urls)

async def main():
    # 从外部文件读取URLs
    with open("/Users/terrancew/Desktop/实习/main/urls.txt", "r") as f:
        urls = [url.strip() for url in f.readlines()]

    batch_size = 5
    num_batches = len(urls) // batch_size + (len(urls) % batch_size > 0)
    title = "/Users/terrancew/Desktop/实习/data/"+str(datetime.now().strftime("%m-%d %H:%M"))+".json"
    
    pbar = tqdm(total=len(urls), desc="处理 URL 进度")

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = start_index + batch_size
        batch_urls = urls[start_index:end_index]
        processed_url_count = await process_batch(batch_urls, title)
        pbar.update(processed_url_count)

    pbar.close()
    print(f"数据已保存到 {title} 文件")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
