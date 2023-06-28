from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json

def scrape_page_info(url):
    # 创建 ChromeOptions 实例，并禁用图片加载
    chrome_options = Options()
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')

    # 创建一个 WebDriver 实例，指定浏览器驱动的路径和 ChromeOptions
    driver = webdriver.Chrome(options=chrome_options)

    # 打开网页
    driver.get(url)

    # 获取页面内容
    page_content = driver.page_source

    soup = BeautifulSoup(page_content, 'html.parser')

    # 提取评论数
    comment_element = soup.find('li', class_='news-detail-position-pinglun')
    comment_number = comment_element.find('a').text.strip()

    # 提取点赞数
    like_element = soup.find('li', class_='news-detail-position-dianzan')
    like_number = like_element.find('a').text.strip()

    authors = soup.find_all('div', class_='author-box')

    author_list = []
    for author in authors:
        author_name = author.find('p', class_='author-name').text.strip()  # 提取作者名字
        author_id = author.find('a', class_='button attention-button').get('data-id')  # 提取 data-id 属性
        author_homepage = f"https://i.yiche.com/u{author_id}/!article/"

        author_info = {
            '作者名字': author_name,
            '作者ID': author_id,
            '作者主页': author_homepage
        }
        author_list.append(author_info)

    # 关闭 WebDriver
    driver.quit()

    # 构建结果字典
    result = {
        '评论数': comment_number,
        '点赞数': like_number,
        '作者列表': author_list
    }

    # 将结果转换为 JSON 格式并返回
    return json.dumps(result, ensure_ascii=False)


# 示例用法
url = 'https://news.yiche.com/xinchexiaoxi/20230521/0081822289.html'
page_info = scrape_page_info(url)
print(page_info)
