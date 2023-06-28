from bs4 import BeautifulSoup
import json

with open("./yiche/data1.html") as file:
    html=file.read()
soup = BeautifulSoup(html,'html.parser')

# 提取评论数
comment_element = soup.find('li', class_='news-detail-position-pinglun')
comment_number = comment_element.find('a').text.strip()
print('评论数:', comment_number)

# 提取点赞数
like_element = soup.find('li', class_='news-detail-position-dianzan')
like_number = like_element.find('a').text.strip()
print('点赞数:', like_number)

authors = soup.find_all('div', class_='author-box')


for author in authors:
    author_name = author.find('p', class_='author-name').text.strip()  # 提取作者名字
    author_id = author.find('a', class_='button attention-button').get('data-id')  # 提取 data-id 属性
    author_homepage = f"https://i.yiche.com/u{author_id}/!article/"
    print('作者名字:', author_name)
    print('作者 ID:', author_id)
    print(author_homepage)