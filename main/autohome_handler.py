import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
#from tqdm import tqdm

chrome_options = Options()
chrome_options.add_argument('--blink-settings=imagesEnabled=false')

def get_text(element):
    return element.text.strip() if element and element.text.strip() else '0'

def scrape_autohome_page_info(url):
    with webdriver.Chrome(options=chrome_options) as driver:
        try:
            #driver.minimize_window()
            driver.get(url)
            
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            view_number = soup.select_one('.post-handle-view strong')
            reply_number = soup.select_one('.post-handle-reply strong')
            praise_number = soup.select_one('.post-assist-praise strong')

            script_tags = soup.find_all('script')
            for script_tag in script_tags:
                script_content = script_tag.string
                if script_content and '__TOPICINFO__' in script_content:
                    topic_member_id = script_content.split("topicMemberId: ",1)[1].split(",")[0].strip()
                    topic_member_name = script_content.split("topicMemberName: '",1)[1].split("'")[0]
                

            result = {
                "平台": "汽车之家",
                "浏览量": get_text(view_number),
                "回复量": get_text(reply_number),
                "点赞量": get_text(praise_number),
                "加精推荐": 'True' if any(soup.find_all('div', class_='stamp orange activate')) else 'False',
                "作者id": topic_member_id,
                "作者": topic_member_name,
                "文章": url
            }
            return result

        except Exception as e:
            print("汽车之家在爬取过程中出现错误:", e)
            return None


def scrape_autohome_urls(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(scrape_autohome_page_info, urls))
    return [result for result in results if result]  # 过滤掉None值

