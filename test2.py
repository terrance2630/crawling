import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

with open("./xhs.html") as f:
  page = f

  soup = BeautifulSoup(page, "html.parser")

# script_tag = soup.find('script', type='application/ld+json')


# json_str = script_tag.string.strip()

# # 提取所需的字段值

# name = re.search(r'"name":\s*"([^"]+)"', json_str).group(1)
# url = re.search(r'"url":\s*"([^"]+)"', json_str).group(1)
# parsed_url = urlparse(url)
# path = parsed_url.path

# # 提取userid
# user_id = path.split("/")[-1]

# author_info = {"作者":name, "作者 id":user_id, "作者主页": url}

script_tag = soup.findAll('script')
# 遍历所有的script标签
for script in script_tag:
    # 获取script标签的文本内容
    script_text = script.text.strip()
    # 使用正则表达式匹配window.__INITIAL_SSR_STATE__ = {...}的内容
    match = re.search(r'window\.__INITIAL_SSR_STATE__\s*=\s*({.*?})', script_text)
    if match:
        # 提取匹配到的内容
        data_json = match.group(1)
        break
# 使用正则表达式提取所需字段的值
likes_match = re.search(r'"likes"\s*:\s*"([^"]+)"', data_json)
collects_match = re.search(r'"collects"\s*:\s*(\d+)', data_json)
share_count_match = re.search(r'"shareCount"\s*:\s*(\d+)', data_json)
comments_match = re.search(r'"comments"\s*:\s*(\d+)', data_json)

# 提取字段的值
likes = likes_match.group(1) if likes_match else None
collects = collects_match.group(1) if collects_match else None
share_count = share_count_match.group(1) if share_count_match else None
comments = comments_match.group(1) if comments_match else None

# 打印提取到的字段值
print('likes:', likes)
print('collects:', collects)
print('share_count:', share_count)
print('comments:', comments)

# script_content = script_tag.string.strip()
# likes_start_index = script_content.find('"likes":') + len('"likes":') + 1
# likes_end_index = script_content.find(',', likes_start_index)
# likes = script_content[likes_start_index:likes_end_index]

# comment_start_index = script_content.find('"comments":') + len('"comments":') + 1
# comment_end_index = script_content.find(',', comment_start_index)
# comment = script_content[comment_start_index:comment_end_index]

# share_start_index = script_content.find('"shareCount":') + len('"shareCount":') + 1
# share_end_index = script_content.find(',', share_start_index)
# share = script_content[share_start_index:share_end_index]

# collect_start_index = script_content.find('"collects":') + len('"collects":') + 1
# collect_end_index = script_content.find(',', collect_start_index)
# collect = script_content[collect_start_index:collect_end_index]

# print(author_info, likes, comment, share, collect)