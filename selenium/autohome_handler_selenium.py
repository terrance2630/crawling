import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm

chrome_options = Options()

chrome_options.add_argument('--blink-settings=imagesEnabled=false')

def scrape_autohome_page_info(url):
    driver = webdriver.Chrome(options=chrome_options)
    driver.minimize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        
        soup = BeautifulSoup(page_source, 'html.parser')

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

        driver.quit()

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
        driver.quit()
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
