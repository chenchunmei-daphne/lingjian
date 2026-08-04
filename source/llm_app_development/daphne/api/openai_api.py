# from dotenv import load_dotenv
import os
from openai import OpenAI
# load_dotenv()  # 从.env文件加载


print("OPENAI_API_KEY exists:", bool(os.getenv('OPENAI_API_KEY')))
print("OPENAI_API_KEY value:", os.getenv('OPENAI_API_KEY')[:10] + "...")  # 只显示前10位
client = OpenAI()


import os
# print(os.environ)  # 打印所有环境变量
if 'qianwen_openai_api' in os.environ:
    print(f"Environment variable qianwen_openai_api exists with value: {os.environ['qianwen_openai_api'][:10]}")
else:
    print("Environment variable qianwen_openai_api does not exist.")


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