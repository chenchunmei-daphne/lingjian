import os
from openai import OpenAI

api_key=os.getenv("qianwen_openai_api")
client = OpenAI(
    api_key=api_key,  # 从阿里云百炼控制台获取
    base_url="https://ws-s6eavmbn4d8prjq0.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",  # 使用官方端点
)

messages = [{"role": "user", "content": "你是谁"}]
completion = client.chat.completions.create(
    model="qwen-turbo",  # 先用基础模型测试
    messages=messages,
)

print(completion.choices[0].message.content)