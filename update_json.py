import json

# 定义已处理的微博链接列表
processed_weibos = [...]  # 这里替换为你实际的已处理微博链接列表

# 定义要更新的 JSON 文件路径
weibo_data_file = 'json_data/weibo_data.json'  # 替换为你的 JSON 文件路径

# 将已处理的微博链接列表保存到 JSON 文件中
with open(weibo_data_file, 'w') as f:
    json.dump(processed_weibos, f)
