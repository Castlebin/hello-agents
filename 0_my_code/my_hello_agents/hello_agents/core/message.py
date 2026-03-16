"""
hello-agents 消息类
定义和大模型交互的消息格式
"""
from datetime import datetime
from typing import Literal, Optional, Dict, Any

from pyarrow import timestamp
from pydantic import BaseModel
from sqlalchemy.testing.suite.test_reflection import metadata

# 定义消息的角色类型，限制其取值
MessageRole = Literal["system", "user", "assistant", "tool"]

class Message(BaseModel):
    "消息类"
    content: str                # 消息内容
    role: MessageRole           # 消息角色
    timestamp: datetime = None  # 消息时间戳
    metadata: Optional[Dict[str, Any]] = None  # 其他元数据
    
    def __init__(self, content: str, role: MessageRole, **kwargs):
        super().__init__(
            content=content,
            role=role,
            timestamp=kwargs.get("timestamp", datetime.now()),
            metadata=kwargs.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转化为字典格式 （OpenAI API 格式）
        """
        return {
            "role": self.role,
            "content": self.content,
        }

    def __str__(self) -> str:
        return f"[{self.role}] {self.content}"
    
    
    