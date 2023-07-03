import concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import requests

cookies = {

}

headers = {
    'authority': 'news.yiche.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    # 'cookie': 'CIGUID=ec5339c8-0db3-4e29-8b6b-67bdff0ccb14; CIGDCID=x4fbmGQCreeHFh6NnEw28MY5jD5p2EXt; auto_id=d14988c50ba839e18a9d96072167a910; UserGuid=ec5339c8-0db3-4e29-8b6b-67bdff0ccb14; Hm_lvt_610fee5a506c80c9e1a46aa9a2de2e44=1687923640; selectcity=110100; selectcityid=201; selectcityName=%E5%8C%97%E4%BA%AC; locatecity=110100; bitauto_ipregion=103.108.231.76%3A%E5%8C%97%E4%BA%AC%E5%B8%82%3B201%2C%E5%8C%97%E4%BA%AC%2Cbeijing; isWebP=true; report-cookie-id=249625994_1688353425149; Hm_lpvt_610fee5a506c80c9e1a46aa9a2de2e44=1688353430',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}


def scrape_yiche_page_info(url):


    try:
        response = requests.get(url, cookies=cookies, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        comment_element = soup.find('li', class_='news-detail-position-pinglun')
        comment_number = comment_element.find('a').text.strip()

        like_element = soup.find('li', class_='news-detail-position-dianzan')
        like_number = like_element.find('a').text.strip()

        

        authors = soup.find_all('div', class_='author-box')

        author_list = []
        for author in authors:
            author_name = author.find('p', class_='author-name').text.strip()
            author_id = author.find('a', class_='button attention-button').get('data-id')
            author_homepage = f"https://i.yiche.com/u{author_id}/!article/"

            author_info = {
                '作者名字': author_name,
                '作者ID': author_id,
                '作者主页': author_homepage
            }
            author_list.append(author_info)


        result = {
            '平台': "易车",
            '评论数': str(comment_number),
            '点赞数': str(like_number),
            '作者列表': str(author_list),
            "文章": str(url)
        }

        return result

    except Exception as e:
        print("易车在爬取过程中出现错误:", e)
        return None


def scrape_yiche_urls(urls):
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_yiche_page_info, url) for url in urls]

        with tqdm(total=len(futures), desc="易车进度") as pbar:
            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())
                pbar.update(1)

    return result

