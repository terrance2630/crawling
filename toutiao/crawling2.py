from selenium import webdriver

# 创建一个 WebDriver 实例，指定浏览器驱动的路径
driver = webdriver.Chrome()



# 打开网页
url = 'https://www.toutiao.com/article/7235891710436459063/?channel=&source=search_tab'
driver.get(url)

# 执行 JavaScript，允许网站执行 JavaScript
driver.execute_script('document.getElementsByTagName("noscript")[0].remove()')

# 获取页面内容
page_content = driver.page_source

with open('./data1.html', 'w', encoding='utf-8') as f:
    f.write(page_content)
print("源代码已保存")

# 在这里可以使用 BeautifulSoup 或其他方法解析页面内容，提取你需要的信息
# ...

# 关闭 WebDriver
driver.quit()
