# my_main.py
#from dotenv import load_dotenv
from my_llm import MyLLM # 注意:这里导入我们自己的类
import os

# 加载环境变量
#load_dotenv()

# 实例化我们重写的客户端，并指定provider
MODELSCOPE_API_BASE_URL = "https://api-inference.modelscope.cn/v1/"
MODELSCOPE_API_KEY = os.getenv('MODELSCOPE_API_KEY')
MODEL_ID = "Qwen/Qwen3.5-35B-A3B"

# 创建LLM实例
llm = MyLLM(
    model=MODEL_ID,
    base_url=MODELSCOPE_API_BASE_URL,
    api_key=MODELSCOPE_API_KEY,
    provider="modelscope",
    timeout=60
)

# 准备消息
messages = [{"role": "user", "content": "你好，请介绍一下你自己。"}]

# 发起调用，think等方法都已从父类继承，无需重写
response_stream = llm.think(messages)

# 打印响应
print("ModelScope Response:")
for chunk in response_stream:
    # chunk在my_llm库中已经打印过一遍，这里只需要pass即可
    # print(chunk, end="", flush=True)
    pass


