import re
from bs4 import BeautifulSoup

def extract_local_storage(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    script_tag = soup.find('script', text=re.compile('localStorage.setItem'))
    if script_tag:
        script_content = script_tag.string
        match = re.search(r'localStorage.setItem\("([^"]+)",\s*JSON\.stringify\((.+)\)\);', script_content)
        if match:
            key = match.group(1)
            value = match.group(2)
            return key, value
    return None

with open('./data0.html', 'r', encoding='utf-8') as f:
    page_source = f.read()
print(extract_local_storage(page_source))