import re

def extract_id(user_url):
    match = re.search(r'the_user_id=(\d+)', user_url)
    if match:
        user_id = match.group(1)
        
    return user_id

user_urls = [
    'https://is.snssdk.com/motor/ugc/profile.html?link_source=share&the_user_id=109778278488&share_token=0558e8d2-5ca5-4c5d-8dd6-82484bd19789',
    'https://is.snssdk.com/motor/ugc/profile.html?link_source=share&the_user_id=92399202649',
    'https://is.snssdk.com/motor/ugc/profile.html?link_source=share&the_user_id=110983199795&share_token=645ac9a5-1de8-4d21-9daa-1bd7b12210a1'
]

user_ids = []
for url in user_urls:
    user_ids.append(extract_id(url))



print(user_ids)
