# 4.3 Plan-and-Solve 范式 智能体的编码实现

#%% 定义提示词
import ast
import os

"""
这个提示词通过以下几点确保了输出的质量和稳定性：

角色设定： “顶级的AI规划专家”，激发模型的专业能力。
任务描述： 清晰地定义了“分解问题”的目标。
格式约束： 强制要求输出为一个 Python 列表格式的字符串，这极大地简化了后续代码的解析工作，使其比解析自然语言更稳定、更可靠。
"""

# 规划器提示词
PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

#%% 规划器
from llm_client import HelloAgentsLLM
class Planner:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def plan(self, question: str) -> list[str]:
        """
        根据用户问题生成一个行动计划。
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        # 为了生成计划，我们构建一个简单的消息列表
        messages = [{"role": "user", "content": prompt}]

        print("--- 正在生成计划 ---")
        # 使用流式输出来获取完整的计划
        response_text = self.llm_client.think(messages=messages) or ""

        print(f"✅ 计划已生成:\n{response_text}")

        # 解析LLM输出的列表字符串
        try:
            # 找到```python和```之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # 使用 ast.literal_eval 来安全地执行字符串，将其转换为 Python 列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []


#%% 执行器与状态管理
"""
在规划器 (Planner) 生成了清晰的行动蓝图后，我们就需要一个执行器 (Executor) 来逐一完成计划中的任务。执行器不仅负责调用大语言模型来解决每个子问题，还承担着一个至关重要的角色：状态管理。它必须记录每一步的执行结果，并将其作为上下文提供给后续步骤，确保信息在整个任务链条中顺畅流动

执行器的提示词与规划器不同。它的目标不是分解问题，而是在已有上下文的基础上，专注解决当前这一个步骤。因此，提示词需要包含以下关键信息：

原始问题： 确保模型始终了解最终目标。
完整计划： 让模型了解当前步骤在整个任务中的位置。
历史步骤与结果： 提供至今为止已经完成的工作，作为当前步骤的直接输入。
当前步骤： 明确指示模型现在需要解决哪一个具体任务。
"""

# 执行器提示词
EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""
# 执行器
class Executor:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def execute(self, question: str, plan: list[str]) -> str:
        """
        根据计划，逐步执行并解决问题。
        """
        history = ""  # 用于存储历史步骤和结果的字符串

        print("\n--- 正在执行计划 ---")

        for i, step in enumerate(plan):
            print(f"\n-> 正在执行步骤 {i + 1}/{len(plan)}: {step}")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",  # 如果是第一步，则历史为空
                current_step=step
            )

            messages = [{"role": "user", "content": prompt}]

            response_text = self.llm_client.think(messages=messages) or ""

            # 更新历史记录，为下一步做准备
            history += f"步骤 {i + 1}: {step}\n结果: {response_text}\n\n"

            print(f"✅ 步骤 {i + 1} 已完成，结果: {response_text}")

        # 循环结束后，最后一步的响应就是最终答案
        final_answer = response_text
        return final_answer


# %% PlanAndSolveAgent 智能体
class PlanAndSolveAgent:
    def __init__(self, llm_client):
        """
        初始化智能体，同时创建规划器和执行器实例。
        """
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        """
        运行智能体的完整流程:先规划，后执行。
        """
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        # 1. 调用规划器生成计划
        plan = self.planner.plan(question)

        # 检查计划是否成功生成
        if not plan:
            print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return

        # 2. 调用执行器执行计划
        final_answer = self.executor.execute(question, plan)

        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")


# --- 5. 主函数入口 ---
if __name__ == '__main__':
    # 使用硅基流动的在线 API 服务
    SILICONFLOW_API_BASE_URL = "https://api.siliconflow.cn/v1"
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")

    API_KEY = SILICONFLOW_API_KEY
    BASE_URL = SILICONFLOW_API_BASE_URL
    MODEL_ID = "deepseek-ai/DeepSeek-R1"

    try:
        llm_client = HelloAgentsLLM(
            model=MODEL_ID,
            apiKey=API_KEY,
            baseUrl=BASE_URL,
            timeout=60
        )
        agent = PlanAndSolveAgent(llm_client)
        question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
        agent.run(question)
    except ValueError as e:
        print(e)

