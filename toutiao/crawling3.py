import requests
from bs4 import BeautifulSoup

# Send a GET request to the webpage
url = 'https://www.toutiao.com/article/7235891710436459063/?channel=&source=search_tab'
response = requests.get(url)

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the elements containing the digg count and comment count
digg_count_element = soup.find('span', class_='like-count')
comment_count_element = soup.find('span', class_='comment-count')

# Extract the digg count and comment count values
digg_count = digg_count_element.get_text() if digg_count_element else 'N/A'
comment_count = comment_count_element.get_text() if comment_count_element else 'N/A'

# Print the results
print('Digg Count:', digg_count)
print('Comment Count:', comment_count)

with open('./data2.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("源代码已保存")
