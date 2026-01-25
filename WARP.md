# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## 仓库概览

本仓库是「Hello-Agents」教程工程：

- 文档内容位于 `docs/`，包含中英文教程章节，对应的章节导航见根目录的 `README.md` / `README_EN.md` 以及 `docs/README.md`。
- 示例代码位于 `code/`，按章节划分子目录。各章节子项目基本相互独立，**没有统一的全局构建或测试命令**，需要在对应子目录下分别安装依赖并运行。

在 `code/` 目录下，主要的多文件应用/服务包括：

- `code/chapter10/weather-mcp-server/`：基于 HelloAgents 的天气 MCP 服务，可作为独立 MCP 服务器运行。
- `code/chapter13/helloagents-trip-planner/`：智能旅行规划全栈示例（FastAPI 后端 + Vue 3 前端），通过 HelloAgents 及 AMap（高德） MCP 工具协同完成行程规划。
- `code/chapter14/helloagents-deepresearch/`：本地化深度研究智能体（FastAPI 后端 + 轻量前端），通过 HelloAgents 工具完成搜索、总结和笔记。
- `code/chapter15/Helloagents-AI-Town/`：赛博小镇 AI NPC 对话系统，包含 FastAPI 后端以及基于 Godot 4 的 GDScript 客户端（脚本位于 `helloagents-ai-town/scripts/`）。

其它章节子目录多为小型示例或实验代码，用于演示特定概念（框架用法、经典 Agent 范式、MCP Demo、RL 训练流程等）。

## 环境与依赖约定

大部分 Python 示例默认：

- 使用 Python ≥ 3.10
- 已通过 PyPI 安装 `hello-agents` 库（代码中常见 `from hello_agents import ...`）。

较完整的子项目在自身目录内声明依赖：

- 使用 `requirements.txt`：如 `code/chapter13/helloagents-trip-planner/backend/`、`code/chapter15/Helloagents-AI-Town/backend/`。
- 使用 `pyproject.toml`：如 `code/chapter10/weather-mcp-server/`、`code/chapter14/helloagents-deepresearch/backend/`。

在修改或运行某个示例时，应切换到对应子目录，在该目录下安装依赖（典型命令为 `pip install -r requirements.txt` 或 `pip install .`）。

## 常用命令

本仓库没有统一的项目启动脚本，下面列出常用子项目的运行方式以及代表性的测试脚本。

### Weather MCP Server（第 10 章）

位置：`code/chapter10/weather-mcp-server/`

安装与运行：

- 安装依赖（参见该目录下 README）：
  - `pip install hello-agents requests`
- 启动 MCP 服务器：
  - `cd code/chapter10/weather-mcp-server`
  - `python server.py`

该服务提供实时天气查询 MCP 接口，可直接调用，或通过 HelloAgents 的 `MCPTool` 使用。

### 智能旅行助手（第 13 章）

#### 后端（FastAPI + HelloAgents）

位置：`code/chapter13/helloagents-trip-planner/backend/`

推荐流程：

- （可选）创建并激活虚拟环境。
- 安装后端依赖：
  - `cd code/chapter13/helloagents-trip-planner/backend`
  - `pip install -r requirements.txt`
- 初始化环境变量：
  - `cp .env.example .env`
  - 修改 `.env`，至少设置：
    - `AMAP_API_KEY`：高德地图 Web 服务密钥
    - `LLM_API_KEY` 或 `OPENAI_API_KEY`：LLM 服务密钥（或配合 `LLM_BASE_URL` / `LLM_MODEL_ID` 使用自建兼容服务）
- 启动 API（带热重载）：
  - `python run.py`
  - 或 `uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000`

启动后可通过 `http://localhost:8000/docs` 查看交互式 API 文档。

#### 前端（Vue 3 + Vite）

位置：`code/chapter13/helloagents-trip-planner/frontend/`

- 安装 Node 依赖：
  - `cd code/chapter13/helloagents-trip-planner/frontend`
  - `npm install`
- 配置高德 Web Key：
  - `echo "VITE_AMAP_WEB_KEY=your_amap_web_key" > .env`
- 启动前端开发服务器：
  - `npm run dev`

### 深度研究智能体（第 14 章）

#### 后端（FastAPI 深度研究服务）

位置：`code/chapter14/helloagents-deepresearch/backend/`

该后端提供一个 `DeepResearchAgent`，通过 HelloAgents 工具完成多轮 Web 检索、任务拆解、总结与笔记写入，并通过 HTTP 暴露出来。

- 安装依赖（基于 `pyproject.toml`）：
  - `cd code/chapter14/helloagents-deepresearch/backend`
  - `pip install .`           # 安装运行时依赖
  - 或 `pip install .[dev]`   # 同时安装 ruff 等开发工具
- 配置环境变量（可用 `.env` 或 shell 环境变量）：关键项见 `src/config.py`：
  - `LLM_PROVIDER`，`LLM_MODEL_ID`，`LLM_API_KEY`，`LLM_BASE_URL`
  - `SEARCH_API`（如 `duckduckgo`、`perplexity`、`tavily` 等）
  - `NOTES_WORKSPACE`（NoteTool 存储 markdown 笔记的目录）
- 启动 API（开发模式）：
  - `cd code/chapter14/helloagents-deepresearch/backend`
  - `python -m src.main`
  - 或在保证 `src` 在 `PYTHONPATH` 中时：`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

关键 HTTP 接口（定义于 `src/main.py`）：

- `GET /healthz`：健康检查
- `POST /research`：执行完整研究流程，返回 Markdown 报告和结构化 TODO 列表
- `POST /research/stream`：以 Server-Sent Events 形式流式返回进度事件与最终报告

#### 前端（最小化 Vue 客户端）

位置：`code/chapter14/helloagents-deepresearch/frontend/`

- 安装依赖：
  - `cd code/chapter14/helloagents-deepresearch/frontend`
  - `npm install`
- 启动开发服务器：
  - `npm run dev`

该前端是对 `/research` 和 `/research/stream` 接口的简单 UI 封装。

### 赛博小镇后端（第 15 章）

位置：`code/chapter15/Helloagents-AI-Town/backend/`

该后端为赛博小镇提供 NPC 列表、对话和状态管理服务，对应文档见 `code/chapter15/Helloagents-AI-Town/README.md` 及相关指南。

- 安装依赖：
  - `cd code/chapter15/Helloagents-AI-Town/backend`
  - `pip install -r requirements.txt`
- 配置环境变量（`.env` 或 shell），为 HelloAgents 提供所需的 LLM 密钥等配置。
- 启动 API：
  - `python main.py`
  - 或 `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- 运行基础 API 自检脚本：
  - `python test_api.py`

该服务提供 NPC 列表、NPC 状态查询、对话与强制刷新等 REST 接口。

### 赛博小镇 Godot 客户端脚本

位置：`code/chapter15/Helloagents-AI-Town/helloagents-ai-town/scripts/`

此目录下的 `README.md` 详细说明了各 GDScript 文件与 Godot 场景的对应关系，以及如何通过 `APIClient` 自动加载节点与 FastAPI 后端交互。

修改或扩展玩法逻辑时：

- 建议统一在 `config.gd` 中维护 API 基础地址以及全局参数（如 `API_BASE_URL`，`NPC_STATUS_UPDATE_INTERVAL` 等）。
- 整体数据流：`player.gd` / `npc.gd` 负责输入与交互检测，`dialogue_ui.gd` 管理对话 UI 并将消息转发给 `api_client.gd`，`main.gd` 负责周期性拉取 NPC 状态并分发给场景中的 NPC。

### 代表性测试脚本

各章节测试方式不统一，多数是可直接运行的 Python 脚本，必要时也可用 `pytest` 指定单个用例。

常用入口包括：

- 经典 Agent 行为测试（第 7 章）：
  - `cd code/chapter7`
  - 直接以脚本方式运行 ReAct Agent 测试：
    - `python test_react_agent.py`
  - 若本地使用 `pytest`，可只跑单个用例：
    - `pytest test_react_agent.py::test_react_agent`
- 天气 MCP Server 联调（第 10 章）：
  - `cd code/chapter10`
  - 确认 `weather-mcp-server/server.py` 能正常启动
  - 运行测试客户端脚本：
    - `python 14_test_weather_server.py`
- RL 训练快速实验（第 11 章）：
  - `cd code/chapter11`
  - `python 00_quick_test.py`  # 使用 `RLTrainingTool` 快速跑一遍 SFT 和 GRPO 流程
- 通用 Agent 行为检查（第 16 章）：
  - `cd code/chapter16/haoye2-UnivesalAgent/outputs/tests`
  - `python test_agent_improvements.py`

## 高层架构说明

### HelloAgents 使用模式

整个仓库在使用 HelloAgents 时有一套比较统一的模式：

- 通过 `HelloAgentsLLM` 创建 LLM 客户端，配置主要由环境变量控制（如 `LLM_PROVIDER`、`LLM_MODEL_ID`、`LLM_API_KEY` 等）。
- 对话智能体一般使用 `SimpleAgent` 或 `ToolAwareSimpleAgent`，通过系统提示词（system prompt）约束行为、角色与输出格式。
- 工具通过 `ToolRegistry` 或 `agent.add_tool(...)` 绑定，常见工具包括：
  - `MCPTool`：对接外部 MCP 服务（如高德地图 amap-mcp-server、自定义天气服务器等）。
  - `SearchTool`：在深度研究后端中调用多种 Web 搜索后端并聚合结果。
  - `NoteTool`：用于将中间结果和报告写入本地 markdown 笔记。
- 多智能体系统（如旅行助手）通过组合多个职责单一的 Agent 完成整体任务，通常共享工具与部分配置。

在扩展功能时，优先在现有 Agent / Service 的基础上增加职责（例如为旅行助手增加新的“餐饮推荐 Agent”，或为深度研究增加新的报告模式），而不是新建完全独立的入口脚本。

### 深度研究后端架构（第 14 章）

核心代码位于 `code/chapter14/helloagents-deepresearch/backend/src/`：

- `config.py`：定义 `Configuration` Pydantic 模型，从环境变量构建配置（`from_env`），集中管理搜索后端、LLM、笔记存储等行为开关与参数。
- `agent.py`：实现 `DeepResearchAgent` 协调器：
  - 基于 `Configuration` 初始化共享 `HelloAgentsLLM` 实例。
  - 视配置决定是否创建 `NoteTool` 并放入共享 `ToolRegistry`，供各子 Agent 统一写入笔记。
  - 基于同一 LLM 创建三个工具感知型 Agent：
    - 规划 Agent（`todo_agent`）：根据主题生成结构化 TODO 任务列表。
    - 总结 Agent（通过工厂函数动态创建）：针对单个任务生成总结，可流式输出。
    - 报告 Agent（`report_agent`）：基于全局状态生成最终 Markdown 报告。
  - 通过 `services.search.dispatch_search` 调用 `SearchTool` 执行 Web 检索，并使用 `services.summarizer.SummarizationService` 对每个任务进行总结。
  - 使用 `services.tool_events.ToolCallTracker` 统一记录工具调用事件，支持流式消费和最终报告落地。
  - 对外提供 `run(topic)`（一次性返回结果）和 `run_stream(topic)`（生成事件流）两种调用方式。
- `models.py`：定义 `SummaryState`、`TodoItem` 等数据结构，用于跟踪研究进度、总结内容、笔记 ID/路径等。
- `services/`：将大流程拆分为可复用的服务：
  - `planner.py`：封装规划 Agent，负责提示词构建与 JSON/工具调用格式的鲁棒解析，并在失败时构造兜底任务。
  - `search.py`：封装 `SearchTool`，支持多后端、结果归一化，并构建给总结 Agent 使用的上下文文本。
  - `summarizer.py`：支持同步和流式两种总结模式，负责剥离 `<think>` 片段、去掉工具调用标记等。
  - 其它模块（`reporter.py`、`notes.py`、`tool_events.py`、`text_processing.py`、`utils.py`）负责报告组装、笔记提示语、工具事件缓冲和文本清洗等辅助功能。
- `main.py`：FastAPI 入口，负责创建应用、挂载 CORS、记录启动配置，并将 HTTP 请求分发给 `DeepResearchAgent`。

修改整体研究行为时，通常应优先修改 `Configuration`、`DeepResearchAgent` 或 `services/` 层，而非 FastAPI 路由本身。

### 智能旅行助手后端架构（第 13 章）

后端目录：`code/chapter13/helloagents-trip-planner/backend/app/`

- `config.py`：基于 `pydantic-settings` 与 `dotenv` 的 `Settings` 模型，优先加载本地 `.env`，同时在存在时兼容上层 `HelloAgents/.env`。启动时会打印关键信息，并校验 `AMAP_API_KEY` 与 LLM 密钥是否配置。
- `api/main.py`：FastAPI 应用：
  - 根据 `Settings.cors_origins` 配置 CORS。
  - 通过 `app.include_router` 将 `api/routes/trip.py`、`poi.py`、`map.py` 注册到 `/api` 前缀下。
  - 提供 `/` 与 `/health` 健康检查接口。
- `agents/trip_planner_agent.py`：多智能体编排核心：
  - 基于 `uvx amap-mcp-server` 创建一次性的共享 `MCPTool`，使用 `AMAP_MAPS_API_KEY` 连接高德 MCP 服务。
  - 基于共享 LLM 创建 4 个 `SimpleAgent`：景点搜索专家、天气专家、酒店推荐专家、行程规划专家，各自带有严格的系统提示词（包括工具调用格式约束和 JSON 输出格式约束）。
  - 运行流程：景点搜索 → 天气查询 → 酒店搜索 → 行程规划，将上游结果以文本形式传递给规划 Agent 生成完整行程 JSON。当解析失败时，构造一个可用但较为简化的兜底行程。
  - 通过 `get_trip_planner_agent()` 暴露单例 `MultiAgentTripPlanner`，供路由层直接调用。
- `services/amap_service.py`：高德 MCP 服务封装层：
  - 使用全局 `MCPTool` 实例，提供 `search_poi`、`get_weather`、`plan_route`、`geocode`、`get_poi_detail` 等方法。
  - 负责低层 MCP 调用与结果解析，是扩展地图相关功能（如新增路线类型、解析更多返回字段）的推荐位置。
- `models/schemas.py`：Pydantic 模型，定义 `TripRequest`、`TripPlan`、`DayPlan` 等请求/响应结构，这些结构在前后端之间复用，对应前端 `types` 目录中的 TS 类型。

前端（`frontend/`）通过 HTTP 调用 `/api` 下的接口，整体数据结构与 Pydantic 模型保持一致。

### 赛博小镇架构（第 15 章）

后端（`code/chapter15/Helloagents-AI-Town/backend/`）：

- 使用 FastAPI 提供 NPC 相关 REST 接口（NPC 列表、NPC 状态、对话、刷新等）。
- 使用 HelloAgents 构建 NPC 对话 Agent，为每个 NPC 维护短期记忆、长期记忆和好感度等状态。
- 通过 `batch_generator.py` 实现批量对话生成逻辑：周期性将所有 NPC 对话合并为一次 LLM 调用，从而显著降低 API 成本（对比逐 NPC 调用）。

Godot 客户端脚本（`helloagents-ai-town/scripts/`）：

- `config.gd`：统一配置 API 地址、更新间隔、调试开关等全局参数。
- `api_client.gd`：封装 HTTP 请求并向其它脚本广播信号，是前端与 FastAPI 后端的中心桥接层。
- `player.gd`、`npc.gd`、`dialogue_ui.gd`、`main.gd`：负责输入处理、NPC 交互、对话 UI 和 NPC 状态轮询等逻辑，具体节点结构与信号流请参考该目录下 `README.md`。

当扩展赛博小镇功能时，推荐：

- 在后端增加或修改 NPC 定义、记忆/好感度逻辑，以及批量生成策略；
- 前端主要聚焦表现层和交互，尽量将“剧情”与“行为决策”留在后端 Agent 中实现。
