"""
6.5.2 三步问答助手
在理解了 LangGraph 的核心概念之后，我们将通过一个实战案例来巩固所学。我们将构建一个简化的问答对话助手，它会遵循一个清晰、固定的三步流程来回答用户的问题：

- 理解 (Understand)：首先，分析用户的查询意图。
- 搜索 (Search)：然后，模拟搜索与意图相关的信息。
- 回答 (Answer)：最后，基于意图和搜索到的信息，生成最终答案。

这个案例将清晰地展示如何定义状态、创建节点以及将它们线性地连接成一个完整的工作流。我们将代码分解为四个核心步骤：定义状态、创建节点、构建图、以及运行应用。
"""
"""
（1）定义全局状态

首先，我们需要定义一个贯穿整个工作流的全局状态。这是一个共享的数据结构，
它在图的每个节点之间传递，作为工作流的持久化上下文。 每个节点都可以读取该结构中的数据，并对其进行更新。
"""
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class SearchState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str      # 经过 LLM 理解后的用户需求总结
    search_query: str    # 优化后用于 Tavily API 的搜索查询
    search_results: str  # Tavily 搜索返回的结果
    final_answer: str    # 最终生成的答案
    step: str            # 标记当前步骤


"""
（2）定义工作流节点
"""
# 先完成项目的初始化
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tavily import TavilyClient

# 加载 .env 文件中的环境变量
# load_dotenv()

os.environ['LLM_MODEL_ID'] = "gpt-4o-mini"
os.environ['LLM_API_KEY'] = os.getenv('free.v36.cm.apiKey')     # 使用替代的 api
os.environ['LLM_BASE_URL'] = os.getenv('free.v36.cm.baseUrl')   # 使用替代的 api


# 初始化模型
# 我们将使用这个 llm 实例来驱动所有节点的智能
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID", "gpt-4o-mini"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    temperature=0.7
)
# 初始化 Tavily 客户端
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


"""
开始一步一步创建上面提到的三个核心节点：
1. 理解
2. 搜索
3. 回答
"""

"""
（1） 理解与查询节点
此节点是工作流的第一步，此节点的职责是理解用户意图，并为其生成一个最优化的搜索查询。
"""
def understand_query_node(state: SearchState) -> SearchState:
    """步骤 1：理解用户查询并生成搜索关键词"""

    # 获取最新的用户消息
    user_message = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break

    understand_prompt = f"""分析用户的查询："{user_message}"

请完成两个任务：
1. 简洁总结用户想要了解什么
2. 生成最适合搜索的关键词（中英文均可，要精准）

格式：
理解：[用户需求总结]
搜索词：[最佳搜索关键词]"""

    response = llm.invoke([SystemMessage(content=understand_prompt)])

    # 提取搜索关键词
    response_text = response.content
    search_query = user_message  # 默认使用原始查询

    if "搜索词：" in response_text:
        search_query = response_text.split("搜索词：")[1].strip()
    elif "搜索关键词：" in response_text:
        search_query = response_text.split("搜索关键词：")[1].strip()

    return {
        "user_query": response.content,
        "search_query": search_query,
        "step": "understood",
        "messages": [AIMessage(content=f"我理解您的需求：{response.content}")]
    }


"""
（2）搜索节点
该节点负责执行智能体的“工具使用”能力，它将调用 Tavily API 进行真实的互联网搜索，并具备基础的错误处理功能。
"""
def tavily_search_node(state: SearchState) -> SearchState:
    """步骤 2：使用 Tavily API 进行真实搜索"""

    search_query = state["search_query"]

    try:
        print(f"🔍 正在搜索: {search_query}")

        # 调用Tavily搜索API
        response = tavily_client.search(
            query=search_query,
            search_depth="basic",
            include_answer=True,
            include_raw_content=False,
            max_results=5
        )

        # 处理搜索结果
        search_results = ""

        # 优先使用Tavily的综合答案
        if response.get("answer"):
            search_results = f"综合答案：\n{response['answer']}\n\n"

        # 添加具体的搜索结果
        if response.get("results"):
            search_results += "相关信息：\n"
            for i, result in enumerate(response["results"][:3], 1):
                title = result.get("title", "")
                content = result.get("content", "")
                url = result.get("url", "")
                search_results += f"{i}. {title}\n{content}\n来源：{url}\n\n"

        if not search_results:
            search_results = "抱歉，没有找到相关信息。"

        return {
            "search_results": search_results,
            "step": "searched",
            "messages": [AIMessage(content=f"✅ 搜索完成！找到了相关信息，正在为您整理答案...")]
        }

    except Exception as e:
        error_msg = f"搜索时发生错误: {str(e)}"
        print(f"❌ {error_msg}")

        return {
            "search_results": f"搜索失败：{error_msg}",
            "step": "search_failed",
            "messages": [AIMessage(content="❌ 搜索遇到问题，我将基于已有知识为您回答")]
        }

"""
（3）回答节点
最后的回答节点能够根据上一步的搜索是否成功，来选择不同的回答策略，具备了一定的弹性。
"""
def generate_answer_node(state: SearchState) -> SearchState:
    """步骤 3：基于搜索结果生成最终答案"""

    # 检查是否有搜索结果
    if state["step"] == "search_failed":
        # 如果搜索失败，基于LLM知识回答
        fallback_prompt = f"""搜索API暂时不可用，请基于您的知识回答用户的问题：

用户问题：{state['user_query']}

请提供一个有用的回答，并说明这是基于已有知识的回答。"""

        response = llm.invoke([SystemMessage(content=fallback_prompt)])

        return {
            "final_answer": response.content,
            "step": "completed",
            "messages": [AIMessage(content=response.content)]
        }

    # 基于搜索结果生成答案
    answer_prompt = f"""基于以下搜索结果为用户提供完整、准确的答案：

用户问题：{state['user_query']}

搜索结果：
{state['search_results']}

请要求：
1. 综合搜索结果，提供准确、有用的回答
2. 如果是技术问题，提供具体的解决方案或代码
3. 引用重要信息的来源
4. 回答要结构清晰、易于理解
5. 如果搜索结果不够完整，请说明并提供补充建议"""

    response = llm.invoke([SystemMessage(content=answer_prompt)])

    return {
        "final_answer": response.content,
        "step": "completed",
        "messages": [AIMessage(content=response.content)]
    }

"""
（4）构建图
我们将所有节点连接起来。
"""
# 构建搜索工作流
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

def create_search_assistant():
    workflow = StateGraph(SearchState)

    # 添加三个节点
    workflow.add_node("understand", understand_query_node)
    workflow.add_node("search", tavily_search_node)
    workflow.add_node("answer", generate_answer_node)

    # 设置线性流程
    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "search")
    workflow.add_edge("search", "answer")
    workflow.add_edge("answer", END)

    # 编译图
    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


# 主函数
import asyncio

async def main():
    """主函数：运行智能搜索助手"""

    # 检查API密钥
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ 错误：请在.env文件中配置TAVILY_API_KEY")
        return

    app = create_search_assistant()

    print("🔍 智能搜索助手启动！")
    print("我会使用Tavily API为您搜索最新、最准确的信息")
    print("支持各种问题：新闻、技术、知识问答等")
    print("(输入 'quit' 退出)\n")

    session_count = 0

    while True:
        user_input = input("🤔 您想了解什么: ").strip()

        if user_input.lower() in ['quit', 'q', '退出', 'exit']:
            print("感谢使用！再见！👋")
            break

        if not user_input:
            continue

        session_count += 1
        config = {"configurable": {"thread_id": f"search-session-{session_count}"}}

        # 初始状态
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_query": "",
            "search_query": "",
            "search_results": "",
            "final_answer": "",
            "step": "start"
        }

        try:
            print("\n" + "=" * 60)

            # 执行工作流
            async for output in app.astream(initial_state, config=config):
                for node_name, node_output in output.items():
                    if "messages" in node_output and node_output["messages"]:
                        latest_message = node_output["messages"][-1]
                        if isinstance(latest_message, AIMessage):
                            if node_name == "understand":
                                print(f"🧠 理解阶段: {latest_message.content}")
                            elif node_name == "search":
                                print(f"🔍 搜索阶段: {latest_message.content}")
                            elif node_name == "answer":
                                print(f"\n💡 最终回答:\n{latest_message.content}")

            print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print(f"❌ 发生错误: {e}")
            print("请重新输入您的问题。\n")


if __name__ == "__main__":
    asyncio.run(main())


""" 一次执行输出  （用户输入：明天我想去北京旅游，请推荐有什么好玩的吗？然后给一些旅游建议）

🔍 智能搜索助手启动！
我会使用Tavily API为您搜索最新、最准确的信息
支持各种问题：新闻、技术、知识问答等
(输入 'quit' 退出)

🤔 您想了解什么: 明天我想去北京旅游，请推荐有什么好玩的吗？然后给一些旅游建议

============================================================
🧠 理解阶段: 我理解您的需求：理解：用户想了解明天在北京的旅游景点和一些旅游建议。  
搜索词：北京旅游景点推荐, Beijing travel attractions, 北京旅游建议, Beijing travel tips
🔍 正在搜索: 北京旅游景点推荐, Beijing travel attractions, 北京旅游建议, Beijing travel tips
🔍 搜索阶段: ✅ 搜索完成！找到了相关信息，正在为您整理答案...

💡 最终回答:
明天在北京的旅游建议和景点推荐如下：

### 主要旅游景点
1. **故宫**：世界上最大的皇宫建筑群，拥有丰富的历史和文化遗产。
2. **长城（慕田峪段）**：这里的长城风景优美，适合游客漫步和拍照。
3. **天坛**：古代皇帝祭天的地方，以其宏伟的建筑和宁静的环境著称。
4. **颐和园**：一个大型的皇家园林，有着美丽的湖泊和园艺设计。
5. **胡同和四合院**：探索北京传统的巷弄和庭院，体验地道的街头小吃。

### 旅游建议
- **行程安排**：建议至少安排4天的时间游览北京的主要景点，这样可以更从容地享受每个地方的魅力。
- **购物推荐**：可以前往王府井大街和潘家园旧货市场，后者以古玩和纪念品而闻名。
- **注意事项**：如果是第一次爬长城，不建议在第一天就去，可能会导致腿部疲劳，影响后续的行程（来源：[TikTok](https://www.tiktok.com/@1beijingtraveler/video/7564330051416689938)）。

### 补充建议
- 事先规划好行程，选择合适的交通工具以节省时间。
- 尝试当地美食，比如北京烤鸭和各种街边小吃。
- 提前预定门票，尤其是故宫和长城等热门景点，以避免排长队。

希望这些信息能帮助你更好地规划明天的行程，享受在北京的美好时光！

============================================================

🤔 您想了解什么: 
"""
