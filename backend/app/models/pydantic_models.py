from pydantic import BaseModel, Field  
from typing import Optional, List, Dict, Any  

class ChatRequest(BaseModel):  
    """聊天请求模型"""  
    query: str = Field(..., description="用户的查询文本")  
    conversation_id: Optional[str] = Field(None, description="会话ID，用于继续已有会话")  
    stream: bool = Field(True, description="是否使用流式响应")  
    flow_type: str = Field("data_analysis", description="流程类型: data_analysis, marketing, complete")  

class ChatResponse(BaseModel):  
    """聊天响应模型"""  
    message_id: str = Field(..., description="消息ID")  
    conversation_id: str = Field(..., description="会话ID")  
    response: str = Field(..., description="系统生成的响应文本")  
    response_type: str = Field(..., description="响应类型: data_analysis, marketing, complete")  

class Message(BaseModel):  
    """消息模型"""  
    id: str = Field(..., description="消息ID")  
    role: str = Field(..., description="消息角色: user, assistant")  
    content: str = Field(..., description="消息内容")  
    created_at: str = Field(..., description="创建时间")  

class ConversationSummary(BaseModel):  
    """会话摘要模型"""  
    id: str = Field(..., description="会话ID")  
    title: str = Field(..., description="会话标题")  
    created_at: str = Field(..., description="创建时间")  
    updated_at: str = Field(..., description="最后更新时间")  
    message_count: int = Field(..., description="消息数量")  