## 6.3 框架二：AgentScope

如果说 AutoGen 的设计哲学是"以对话驱动协作"，那么 AgentScope 则代表了另一种技术路径：<strong>工程化优先的多智能体平台</strong>。AgentScope 由阿里巴巴达摩院开发，专门为构建大规模、高可靠性的多智能体应用而设计。它不仅提供了直观易用的编程接口，更重要的是内置了分布式部署、容错恢复、可观测性等企业级特性，使其特别适合构建需要长期稳定运行的生产环境应用。

### 6.3.1 AgentScope 的设计

与 AutoGen 相比，AgentScope 的核心差异在于其<strong>消息驱动的架构设计</strong>和<strong>工业级的工程实践</strong>。如果说 AutoGen 更像是一个灵活的"对话工作室"，那么 AgentScope 就是一个完整的"智能体操作系统"，为开发者提供了从开发、测试到部署的全生命周期支持。与许多框架采用的继承式设计不同，AgentScope 选择了<strong>组合式架构</strong>和<strong>消息驱动模式</strong>。这种设计不仅增强了系统的模块化程度，也为其出色的并发性能和分布式能力奠定了基础。

（1）分层架构体系

如图6.2所示，AgentScope 采用了清晰的分层模块化设计，从底层的基础组件到上层的应用编排，形成了一个完整的智能体开发生态。

<div align="center">
  <img src="https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/6-figures/03.png" alt="" width="90%"/>
  <p>图 6.2 AgentScope架构图</p>
</div>

在这个架构中，最底层是<strong>基础组件层 (Foundational Components)</strong>，它为整个框架提供了核心的构建块。`Message` 组件定义了统一的消息格式，支持从简单的文本交互到复杂的多模态内容；`Memory` 组件提供了短期和长期记忆管理；`Model API` 层抽象了对不同大语言模型的调用；而 `Tool` 组件则封装了智能体与外部世界交互的能力。

在基础组件之上，<strong>智能体基础设施层 (Agent-level Infrastructure)</strong> 提供了更高级的抽象。这一层不仅包含了各种预构建的智能体（如浏览器使用智能体、深度研究智能体），还实现了经典的 ReAct 范式，支持智能体钩子、并行工具调用、状态管理等高级特性。特别值得注意的是，这一层原生支持<strong>异步执行与实时控制</strong>，这是 AgentScope 相比其他框架的一个重要优势。

<strong>多智能体协作层 (Multi-Agent Cooperation)</strong> 是 AgentScope 的核心创新所在。`MsgHub` 作为消息中心，负责智能体间的消息路由和状态管理；而 `Pipeline` 系统则提供了灵活的工作流编排能力，支持顺序、并发等多种执行模式。这种设计使得开发者可以轻松构建复杂的多智能体协作场景。

最上层的<strong>开发与部署层 (Deployment & Devvelopment)</strong>则体现了 AgentScope 对工程化的重视。`AgentScope Runtime` 提供了生产级的运行时环境，而 `AgentScope Studio` 则为开发者提供了完整的可视化开发工具链。

（2）消息驱动

AgentScope 的核心创新在于其<strong>消息驱动架构</strong>。在这个架构中，所有的智能体交互都被抽象为<strong>消息</strong>的发送和接收，而不是传统的函数调用。

```python
from agentscope.message import Msg

# 消息的标准结构
message = Msg(
    name="Alice",           # 发送者名称
    content="Hello, Bob!",  # 消息内容
    role="user",           # 角色类型
    metadata={             # 元数据信息
        "timestamp": "2024-01-15T10:30:00Z",
        "message_type": "text",
        "priority": "normal"
    }
)
```

将消息作为交互的基础单元，带来了几个关键优势：

- <strong>异步解耦</strong>: 消息的发送方和接收方在时间上解耦，无需相互等待，天然支持高并发场景。
- <strong>位置透明</strong>: 智能体无需关心另一个智能体是在本地进程还是在远程服务器上，消息系统会自动处理路由。
- <strong>可观测性</strong>: 每一条消息都可以被记录、追踪和分析，极大地简化了复杂系统的调试与监控。
- <strong>可靠性</strong>: 消息可以被持久化存储和重试，即使系统出现故障，也能保证交互的最终一致性，提升了系统的容错能力。

（3）智能体生命周期管理

在 AgentScope 中，每个智能体都有明确的生命周期（初始化、运行、暂停、销毁等），并基于一个统一的基类 `AgentBase` 来实现。开发者通常只需要关注其核心的 `reply` 方法。

```python
from agentscope.agents import AgentBase

class CustomAgent(AgentBase):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        # 智能体初始化逻辑
    
    def reply(self, x: Msg) -> Msg:
        # 智能体的核心响应逻辑
        response = self.model(x.content)
        return Msg(name=self.name, content=response, role="assistant")
    
    def observe(self, x: Msg) -> None:
        # 智能体的观察逻辑（可选）
        self.memory.add(x)
```

这种设计模式分离了智能体的内部逻辑与外部通信，开发者只需在 `reply` 方法中定义智能体“思考和回应”的方式即可。

（4）消息传递机制

AgentScope 内置了一个<strong>消息中心 (MsgHub)</strong>，它是整个消息驱动架构的中枢。MsgHub 不仅负责消息的路由和分发，还集成了持久化和分布式通信等高级功能，它有以下这些特点。

- <strong>灵活的消息路由</strong>: 支持点对点、广播、组播等多种通信模式，可以构建灵活复杂的交互网络。
- <strong>消息持久化</strong>: 能够将所有消息自动保存到数据库（如 SQLite, MongoDB），确保了长期运行任务的状态可以被恢复。
- <strong>原生分布式支持</strong>: 这是 AgentScope 的标志性特性。智能体可以被部署在不同的进程或服务器上，`MsgHub` 会通过 RPC（远程过程调用）自动处理跨节点的通信，对开发者完全透明。

这些由底层架构提供的工程化能力，使得 AgentScope 在处理需要高并发、高可靠性的复杂应用场景时，比传统的对话驱动框架更具优势。当然，这也要求开发者理解并适应消息驱动的异步编程范式。
