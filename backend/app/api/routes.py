from fastapi import APIRouter, HTTPException, Depends, Header  
from typing import Optional, List  
from uuid import uuid4  
from sse_starlette.sse import EventSourceResponse  

from app.models.pydantic_models import ChatRequest, ChatResponse  
from app.api.dependencies import get_current_user  
from app.db.crud import list_conversations, get_conversation_by_id, get_conversation_messages  
from app.core.logger import logger  
from app.services.chat_service import IntegratedChatService  

router = APIRouter()  

# Redis客户端依赖  
async def get_chat_service():  
    from app.db.session import db  
    service = IntegratedChatService(db.redis)  
    return service  

@router.post("/query", response_model=Optional[ChatResponse])  
async def chat_query(  
    request: ChatRequest,  
    current_user: dict = Depends(get_current_user),  
    chat_service: IntegratedChatService = Depends(get_chat_service)  
):  
    """聊天查询接口 - 集成数据分析和营销战略流程"""  
    try:  
        # 详细的日志记录  
        logger.info(f"查询请求 - 用户: {current_user['id']}, 查询: {request.query}")  
        logger.info(f"Stream模式: {request.stream}, 流程类型: {request.flow_type}")  
        
        if not request.query.strip():  
            raise HTTPException(status_code=400, detail="查询内容不能为空")  
        
        # 如果请求流式响应  
        if request.stream:  
            # 创建新会话消息  
            conversation, message_id = await chat_service.create_chat_message(  
                user_id=current_user["id"],  
                query=request.query,  
                flow_type=request.flow_type,  
                conversation_id=request.conversation_id  
            )  
            
            # 设置响应头，包含会话ID和消息ID  
            headers = {  
                "X-Conversation-ID": str(conversation["id"]),  
                "X-Message-ID": str(message_id),  
                "Cache-Control": "no-cache",  
                "Connection": "keep-alive"  
            }  
            
            # 返回SSE响应  
            return EventSourceResponse(  
                chat_service.generate_stream_response(  
                    user_id=current_user["id"],  
                    query=request.query,  
                    conversation_id=conversation["id"],  
                    message_id=message_id,  
                    flow_type=request.flow_type  
                ),  
                headers=headers,  
                media_type="text/event-stream"  
            )  
        
        # 非流式响应处理  
        response = await chat_service.generate_response(  
            user_id=current_user["id"],  
            query=request.query,  
            flow_type=request.flow_type,  
            conversation_id=request.conversation_id  
        )  
        
        # 处理 response["text"] 可能是 CrewOutput 对象的情况  
        response_text = response["text"]  
        if hasattr(response_text, 'raw'):  
            response_text = response_text.raw  
        elif not isinstance(response_text, str):  
            response_text = str(response_text)  
        
        # 构建标准响应格式，确保使用处理后的字符串  
        return ChatResponse(  
            message_id=response["message_id"],  
            conversation_id=response["conversation_id"],  
            response=response_text,  
            response_type=response.get("type", request.flow_type)  
        )  
    except Exception as e:  
        logger.error(f"处理查询时发生错误: {str(e)}", exc_info=True)  
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")   

@router.get("/conversations")  
async def list_user_conversations(  
    current_user: dict = Depends(get_current_user),  
    limit: int = 10,  
    offset: int = 0  
):  
    """获取用户的会话列表"""  
    try:  
        conversations = await list_conversations(current_user["id"], limit, offset)  
        return conversations  
    except Exception as e:  
        logger.error(f"获取会话列表时发生错误: {str(e)}", exc_info=True)  
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")  

@router.get("/conversations/{conversation_id}")  
async def get_conversation_detail(  
    conversation_id: str,  
    current_user: dict = Depends(get_current_user)  
):  
    """获取特定会话的详细信息"""  
    try:  
        # 获取会话  
        conversation = await get_conversation_by_id(conversation_id)  
        if not conversation:  
            raise HTTPException(status_code=404, detail="会话不存在")  
        
        # 检查是否是用户自己的会话  
        if conversation["user_id"] != current_user["id"]:  
            raise HTTPException(status_code=403, detail="无权访问此会话")  
        
        # 获取会话消息  
        messages = await get_conversation_messages(conversation_id)  
        
        # 构建响应  
        return {  
            "id": conversation["id"],  
            "title": conversation["title"],  
            "created_at": conversation["created_at"],  
            "updated_at": conversation["updated_at"],  
            "messages": messages  
        }  
    except HTTPException:  
        raise  
    except Exception as e:  
        logger.error(f"获取会话详情时发生错误: {str(e)}", exc_info=True)  
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")  