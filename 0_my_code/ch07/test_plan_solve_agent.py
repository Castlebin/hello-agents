# test_plan_solve_agent.py
#from dotenv import load_dotenv
import os

from hello_agents.core.llm import HelloAgentsLLM
from my_plan_solve_agent import MyPlanAndSolveAgent

# 加载环境变量
#load_dotenv()

# 创建LLM实例
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

# 创建自定义PlanAndSolveAgent
agent = MyPlanAndSolveAgent(
    name="我的规划执行助手",
    llm=llm
)

# 测试复杂问题
question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"

result = agent.run(question)
print(f"\n最终结果: {result}")

# 查看对话历史
print(f"对话历史: {len(agent.get_history())} 条消息")
