from bs4 import BeautifulSoup
import json

with open("./17.html") as file:
    html=file.read()
soup = BeautifulSoup(html,'html.parser')

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

        # 打印结果
        print("topicMemberId:", topic_member_id)
        print("topicMemberName:", topic_member_name)
        break