from bs4 import BeautifulSoup

with open("./qczj-selenium-data.html") as file:
    html=file.read()
soup = BeautifulSoup(html,'html.parser')

praise_element = soup.select_one('.post-assist-praise strong')
praise_number = praise_element.text if praise_element else "Praise number not found."
print(praise_number)