import concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests

cookies = {
    'fvlid': '1687835308440U2rirn6ip9',
    'sessionid': 'F2F81D7E-B512-4E23-A6F3-1B87BBE2734F%7C%7C2023-06-27+11%3A08%3A47.499%7C%7C0',
    'autoid': '80c2bd907ad9987880b98b352d410cce',
    'area': '999999',
    '__ah_uuid_ng': 'c_F2F81D7E-B512-4E23-A6F3-1B87BBE2734F',
    'historybbsName4': 'c-6960%7C%E5%B9%BF%E6%B1%BD%E4%BC%A0%E7%A5%BAA79',
    'sessionip': '103.108.231.76',
    'v_no': '1',
    'visit_info_ad': 'F2F81D7E-B512-4E23-A6F3-1B87BBE2734F||1F9CD0C9-39C3-4F63-9CBF-2F5B3047B9CC||-1||-1||1',
    'ref': '0%7C0%7C0%7C0%7C2023-06-30+17%3A49%3A11.941%7C2023-06-27+11%3A08%3A47.499',
    'ahrlid': '1688118549093v3M4cwEEHb-1688118553111',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Cookie': 'fvlid=1687835308440U2rirn6ip9; sessionid=F2F81D7E-B512-4E23-A6F3-1B87BBE2734F%7C%7C2023-06-27+11%3A08%3A47.499%7C%7C0; autoid=80c2bd907ad9987880b98b352d410cce; area=999999; __ah_uuid_ng=c_F2F81D7E-B512-4E23-A6F3-1B87BBE2734F; historybbsName4=c-6960%7C%E5%B9%BF%E6%B1%BD%E4%BC%A0%E7%A5%BAA79; sessionip=103.108.231.76; v_no=1; visit_info_ad=F2F81D7E-B512-4E23-A6F3-1B87BBE2734F||1F9CD0C9-39C3-4F63-9CBF-2F5B3047B9CC||-1||-1||1; ref=0%7C0%7C0%7C0%7C2023-06-30+17%3A49%3A11.941%7C2023-06-27+11%3A08%3A47.499; ahrlid=1688118549093v3M4cwEEHb-1688118553111',
    'If-Modified-Since': 'Fri, 30 Jun 2023 07:29:20 GMT',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}


def scrape_autohome_page_info(url):
    
    try:
        response = requests.get(
            url,
            cookies=cookies,
            headers=headers,
)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        view_span = soup.select_one('.post-handle-view strong')
        reply_span = soup.select_one('.post-handle-reply strong')
        praise_span = soup.select_one('.post-assist-praise strong')
        # 找到所有的<script>标签
        script_tags = soup.find_all('script')

        # 遍历所有的<script>标签
        for script_tag in script_tags:
            script_content = script_tag.string
            if script_content is not None and '__TOPICINFO__' in script_content:
                # 使用字符串操作提取topicMemberId和topicMemberName的值
                topic_member_id_start = script_content.find("topicMemberId: ") + len("topicMemberId: ")
                topic_member_id_end = script_content.find(",", topic_member_id_start)
                topic_member_id = script_content[topic_member_id_start:topic_member_id_end].strip()

                topic_member_name_start = script_content.find("topicMemberName: '") + len("topicMemberName: '")
                topic_member_name_end = script_content.find("'", topic_member_name_start)
                topic_member_name = script_content[topic_member_name_start:topic_member_name_end]


        view_number = view_span.text if view_span else '0'
        reply_number = reply_span.text if reply_span else '0'
        praise_number = praise_span.text if praise_span and praise_span.text else '0'
        author_id = topic_member_id
        author_title = topic_member_name

        
        if soup.find_all('div', class_='stamp orange'):
            recommand = 'True'
        else:
            recommand = 'False'


        temp = {
            "平台": "汽车之家",
            "浏览量": str(view_number),
            "回复量": str(reply_number),
            "点赞量": str(praise_number),
            "加精推荐": str(recommand),
            "作者id": str(author_id),
            "作者": str(author_title),
            "文章": str(url)
        }

        return temp

    except Exception as e:
        print("汽车之家在爬取过程中出现错误:", e)
        
        return None


def scrape_autohome_urls(urls):
    result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_autohome_page_info, url) for url in urls]

        with tqdm(total=len(futures), desc="汽车之家进度") as pbar:
            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())
                pbar.update(1)

    return result
