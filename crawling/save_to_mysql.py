import mysql.connector

# 创建 MySQL 连接
cnx = mysql.connector.connect(
    host='your_host',
    user='your_username',
    password='your_password',
    database='your_database'
)

cursor = cnx.cursor()

# 创建表格
create_table_query = """
CREATE TABLE IF NOT EXISTS autohome_data (
    platform VARCHAR(255),
    views VARCHAR(255),
    comments VARCHAR(255),
    likes VARCHAR(255),
    recommended VARCHAR(255),
    user_id VARCHAR(255),
    username VARCHAR(255),
    article_link TEXT
)
"""
cursor.execute(create_table_query)

# 插入数据
for item in data:
    insert_query = """
    INSERT INTO autohome_data (
        platform,
        views,
        comments,
        likes,
        recommended,
        user_id,
        username,
        article_link
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        item['平台'],
        item['浏览数'],
        item['评论数'],
        item['点赞数'],
        item['加精推荐'],
        item['用户id'],
        item['用户名'],
        item['文章']
    )
    cursor.execute(insert_query, values)

# 提交事务
cnx.commit()

# 关闭游标和连接
cursor.close()
cnx.close()