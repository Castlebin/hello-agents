# test_reflection_agent.py
#from dotenv import load_dotenv
import os

from hello_agents import HelloAgentsLLM
from my_reflection_agent import MyReflectionAgent

#load_dotenv()
# 创建LLM实例
# 实例化我们重写的客户端，并指定provider
MODELSCOPE_API_BASE_URL = "https://api-inference.modelscope.cn/v1/"
MODELSCOPE_API_KEY = os.getenv('MODELSCOPE_API_KEY')
MODEL_ID = "Qwen/Qwen3.5-35B-A3B"

# 创建LLM实例
llm = HelloAgentsLLM(
    model=MODEL_ID,
    base_url=MODELSCOPE_API_BASE_URL,
    api_key=MODELSCOPE_API_KEY,
    provider="modelscope",
    timeout=100
)

# 测试 1 
# 使用默认通用提示词
general_agent = MyReflectionAgent(name="我的反思助手", llm=llm, max_iterations=7)
# 测试使用
result = general_agent.run("写一篇关于人工智能发展历程的简短文章")



# 测试 2 
# Python 专家
# 使用自定义代码生成提示词（类似第四章）
code_prompts = {
    "initial": "你是Python专家，请编写函数:{task}",
    "reflect": "请审查代码的算法正确性和执行效率:\n任务:{task}\n代码:{content}, 请分析这个回答的质量，指出不足之处，并提出具体的改进建议。如果回答已经很好，请回答\"无需改进\"",
    "refine": "请根据反馈优化代码:\n任务:{task}\n上一轮回答:{last_attempt}\n反馈意见:{feedback}"
}
code_agent = MyReflectionAgent(
    name="我的代码生成助手",
    llm=llm,
    custom_prompts=code_prompts,
    max_iterations=5
)
code_agent.run("写一个快速排序算法")

