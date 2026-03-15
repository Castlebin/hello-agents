# 4.2.3 ReAct 范式 智能体的编码实现

#%% 1. 系统提示词设计
# 提示词是整个 ReAct 机制的基石，它为大语言模型提供了行动的操作指令。
# 我们需要精心设计一个模板，它将动态地插入可用工具、用户问题以及中间步骤的交互历史。
# ReAct 提示词模板
"""
这个模板定义了智能体与LLM之间交互的规范：

角色定义： “你是一个有能力调用外部工具的智能助手”，设定了LLM的角色。
工具清单 ({tools})： 告知LLM它有哪些可用的“手脚”。
格式规约 (Thought/Action)： 这是最重要的部分，它强制LLM的输出具有结构性，使我们能通过代码精确解析其意图。
动态上下文 ({question}/{history})： 将用户的原始问题和不断累积的交互历史注入，让LLM基于完整的上下文进行决策。
"""
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
    - `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
    - `Finish[最终答案]`:当你认为已经获得最终答案时。
    - 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""

#%% 2. 核心循环的实现
from llm_client import HelloAgentsLLM
from tools import ToolExecutor, search
import re

"""
ReActAgent 的核心是一个循环，它不断地“格式化提示词 -> 调用LLM -> 执行动作 -> 整合结果”，直到任务完成或达到最大步数限制。
"""
class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(tools=tools_desc, question=question, history=history_str)

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            if not response_text:
                print("错误：LLM未能返回有效响应。");
                break

            thought, action = self._parse_output(response_text)
            if thought: print(f"🤔 思考: {thought}")
            if not action: print("警告：未能解析出有效的Action，流程终止。"); break

            # 如果是Finish指令，提取最终答案并结束
            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer = self._parse_action_input(action)
                print(f"🎉 最终答案: {final_answer}")
                return final_answer

            # 解析 Action 指令，提取工具名称和输入参数
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                self.history.append("Observation: 无效的Action格式，请检查。");
                continue

            print(f"🎬 行动: {tool_name}[{tool_input}]")
            tool_function = self.tool_executor.getTool(tool_name)
            observation = tool_function(tool_input) if tool_function else f"错误：未找到名为 '{tool_name}' 的工具。"

            print(f"👀 观察: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        return (match.group(1), match.group(2)) if match else (None, None)

    def _parse_action_input(self, action_text: str):
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        return match.group(1) if match else ""


#%% 测试一下
import os
# 使用硅基流动的在线 API 服务
SILICONFLOW_API_BASE_URL = "https://api.siliconflow.cn/v1"
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")

API_KEY = SILICONFLOW_API_KEY
BASE_URL = SILICONFLOW_API_BASE_URL
MODEL_ID = "Qwen/Qwen3-VL-32B-Thinking" 

if __name__ == '__main__':
    llm = HelloAgentsLLM(
        model=MODEL_ID,
        apiKey=API_KEY,
        baseUrl=BASE_URL,
        timeout=60
    )
    tool_executor = ToolExecutor()
    search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    tool_executor.registerTool("Search", search_desc, search)
    
    agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)
    
    # 模型不太行啊，老是查 2023年，调用工具生成的搜索词里也非要带 2023年，导致搜索结果里都是 2023年的信息，完全无法回答这个问题。
    # 忍无可忍，给问题里直接加上当前年份，看看它能不能自己意识到这个问题了。（效果好一点了，蠢模型！）
    # question = "华为最新的手机是哪一款？它的主要卖点是什么？"
    question = "华为最新的手机是哪一款？它的主要卖点是什么？当前是 2026年了！"
    agent.run(question)

