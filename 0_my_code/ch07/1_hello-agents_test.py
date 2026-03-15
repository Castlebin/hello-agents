# 7.1.3 快速体验 hello_agents 框架
from hello_agents import SimpleAgent, HelloAgentsLLM
import os


# 使用 MODELSCOPE 作为 LLM 服务提供商
MODELSCOPE_API_BASE_URL = "https://api-inference.modelscope.cn/v1/"
MODELSCOPE_API_KEY = os.getenv('MODELSCOPE_API_KEY')
MODEL_ID = "Qwen/Qwen3.5-35B-A3B"

# 创建LLM实例
llm = HelloAgentsLLM(
    model=MODEL_ID,
    base_url=MODELSCOPE_API_BASE_URL,
    api_key=MODELSCOPE_API_KEY,
    provider="modelscope",
    timeout=60
)

# 创建SimpleAgent
agent = SimpleAgent(
    name="AI助手",
    llm=llm,
    system_prompt="你是一个有用的AI助手"
)

# 基础对话
response = agent.run("你好！请介绍一下自己")
print(response)


# 添加工具功能（可选）
from hello_agents.tools import CalculatorTool
calculator = CalculatorTool()
# 需要实现7.4.1的MySimpleAgent进行调用，后续章节会支持此类调用方式
# agent.add_tool(calculator)

response = agent.run("请帮我计算 2 + 3 * 4")
print(response)

# 查看对话历史
print(f"历史消息数: {len(agent.get_history())}")

