import asyncio  
import json  
import time  
import re  
from typing import Dict, Tuple, Optional, AsyncIterable, Any  
from uuid import uuid4  

from app.core.logger import logger  
from app.db.crud import create_conversation, create_message, update_message, get_conversation_by_id, update_conversation_title  
from app.flows.flow_manager import FlowManager  
from app.utils.memory_manager import RedisMemoryManager  
from app.db.session import db  

class IntegratedChatService:  
    """集成聊天服务 - 处理消息创建、流式响应和常规响应"""  
    
    def __init__(self, redis_client):  
        self.flow_manager = FlowManager(redis_client)  
        self.memory_manager = RedisMemoryManager(redis_client)  
        
    async def create_chat_message(  
        self,  
        user_id: int,  
        query: str,  
        flow_type: str = "data_analysis",  
        conversation_id: Optional[str] = None  
    ) -> Tuple[Dict, str]:  
        """创建新的会话消息"""  
        # 如果没有提供conversation_id，创建新会话  
        if not conversation_id:  
            conversation = await create_conversation(user_id, query[:30] + "..." if len(query) > 30 else query)  
            conversation_id = conversation["id"]  
        else:  
            conversation = await get_conversation_by_id(conversation_id)  
            if not conversation:  
                raise ValueError(f"会话ID {conversation_id} 不存在")  
        
        # 创建新消息  
        message_id = str(uuid4())  
        await create_message(  
            conversation_id=conversation_id,  
            message_id=message_id,  
            role="user",  
            content=query  
        )  
        
        # 创建空的回复消息，等待后续更新  
        reply_id = message_id + "_reply"  
        await create_message(  
            conversation_id=conversation_id,  
            message_id=reply_id,  
            role="assistant",  
            content=""  
        )  
        
        # 将用户消息保存到Redis内存  
        await self.memory_manager.append_message(  
            conversation_id=conversation_id,  
            role="user",  
            content=query  
        )  
        
        return conversation, reply_id  
    
    async def update_conversation_title(self, conversation_id: str, query: str):  
        """异步更新会话标题"""  
        try:  
            # 获取当前会话  
            conversation = await get_conversation_by_id(conversation_id)  
            if not conversation or conversation["title"] != "New Conversation":  
                return  # 如果会话不存在或已有自定义标题，则不更新  
            
            # 生成新标题 (可以根据需要使用LLM生成更好的标题)  
            new_title = query[:30] + "..." if len(query) > 30 else query  
            
            # 更新会话标题  
            await update_conversation_title(conversation_id, new_title)  
            logger.info(f"已更新会话 {conversation_id} 的标题为: {new_title}")  
        except Exception as e:  
            logger.error(f"更新会话标题时出错: {str(e)}")  
    
    async def generate_stream_response(  
        self,  
        user_id: int,  
        query: str,  
        conversation_id: Optional[str] = None,  
        message_id: Optional[str] = None,  
        flow_type: str = "data_analysis"  
    ) -> AsyncIterable[str]:  
        """生成流式响应 - 使用SSE格式返回处理结果"""  
        total_start_time = time.time()  
        
        # 如果没有提供conversation_id和message_id，创建它们  
        if not conversation_id or not message_id:  
            conversation, message_id = await self.create_chat_message(  
                user_id=user_id,  
                query=query,  
                flow_type=flow_type,  
                conversation_id=conversation_id  
            )  
            conversation_id = conversation["id"]  
        
        try:  
            # 发送处理中消息  
            processing_data = {  
                'text': "正在处理您的问题，请稍候...",  
                'conversation_id': str(conversation_id),  
                'type': flow_type  
            }  
            yield f"data: {json.dumps(processing_data, ensure_ascii=False)}\n\n"  
            
            # 创建作业ID  
            job_id = str(uuid4())  
            
            # 启动流程处理，但不等待完成  
            flow_task = asyncio.create_task(  
                self.flow_manager.execute_flow(  
                    flow_type=flow_type,  
                    job_id=job_id,  
                    query=query,  
                    user_id=user_id,  
                    conversation_id=conversation_id  
                )  
            )  
            
            # 初始化进度和输出变量  
            progress = 0  
            current_output = ""  
            segments = []  
            
            # 监控作业进度并发送更新  
            while not flow_task.done():  
                # 获取当前进度和输出  
                job_progress = await self.flow_manager.get_job_progress(job_id)  
                job_output = await self.flow_manager.get_job_current_output(job_id)  
                
                # 如果有新内容，分段并逐段发送  
                if job_output != current_output:  
                    # 计算新增内容  
                    new_content = job_output[len(current_output):]  
                    current_output = job_output  
                    
                    # 切分新内容进行流式输出  
                    if new_content:  
                        # 分段策略：优先按段落，其次按句子，最后按固定长度  
                        new_segments = self._split_content(new_content)  
                        segments.extend(new_segments)  
                        
                        # 逐段发送  
                        for segment in new_segments:  
                            await asyncio.sleep(0.05)  # 短暂延迟，模拟打字效果  
                            
                            # 发送累积的文本  
                            response_data = {  
                                'text': current_output,  
                                'conversation_id': str(conversation_id),  
                                'progress': job_progress,  
                                'type': flow_type  
                            }  
                            yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"  
                
                # 如果只有进度变化，也发送更新  
                elif job_progress > progress:  
                    progress = job_progress  
                    response_data = {  
                        'text': current_output,  
                        'conversation_id': str(conversation_id),  
                        'progress': progress,  
                        'type': flow_type  
                    }  
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"  
                
                # 短暂等待，减轻服务器负担  
                await asyncio.sleep(0.5)  
            
            # 获取最终结果  
            try:  
                full_response = await flow_task
                full_response = self._process_crew_output(full_response)   
            except Exception as e:  
                logger.error(f"获取流程结果时出错: {str(e)}")  
                full_response = f"处理您的请求时出现错误: {str(e)}"  
            
            # 更新消息  
            if message_id:  
                await update_message(  
                    message_id=message_id,  
                    content=full_response  
                )  
            
            # 发送完成消息  
            final_data = {  
                'text': full_response,  
                'conversation_id': str(conversation_id),  
                'end': True,  
                'message_id': message_id,  
                'type': flow_type,  
                'duration': round(time.time() - total_start_time, 2)  
            }  
            yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"  
            
            # 异步更新会话标题  
            asyncio.create_task(  
                self.update_conversation_title(conversation_id, query)  
            )  
            
        except Exception as e:  
            # 记录错误  
            logger.error(f"生成流式响应时出错: {str(e)}", exc_info=True)  
            
            # 发送错误消息  
            error_data = {  
                'text': f"处理您的请求时出错: {str(e)}",  
                'conversation_id': str(conversation_id),  
                'end': True,  
                'error': True  
            }  
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"  
            
            # 更新消息记录错误  
            if message_id:  
                await update_message(  
                    message_id=message_id,  
                    content=f"系统错误: {str(e)}"  
                )  
    
    def _split_content(self, content: str) -> list:  
        """将内容分段以便流式输出"""  
        segments = []  
        
        # 首先按段落分割  
        paragraphs = content.split('\n\n')  
        for paragraph in paragraphs:  
            if not paragraph.strip():  
                continue  
            
            # 对长段落进行进一步分割  
            if len(paragraph) > 100:  
                # 按句子分割 (中文句号、问号、感叹号、英文句号加空格)  
                sentences = re.split(r'([。！？\.!?]\s*)', paragraph)  
                
                # 将句子和标点符号重新组合  
                i = 0  
                while i < len(sentences) - 1:  
                    if i + 1 < len(sentences):  
                        segments.append(sentences[i] + sentences[i+1])  
                    i += 2  
                    
                # 处理最后一个可能没有标点的句子  
                if i < len(sentences):  
                    segments.append(sentences[i])  
            else:  
                segments.append(paragraph)  
        
        # 如果分段太少，进一步拆分  
        if len(segments) < 3 and len(content) > 100:  
            new_segments = []  
            for segment in segments:  
                if len(segment) > 50:  
                    # 按逗号、分号等次要标点分割  
                    parts = re.split(r'([，,；;：:]\s*)', segment)  
                    
                    # 将短语和标点符号重新组合  
                    i = 0  
                    while i < len(parts) - 1:  
                        if i + 1 < len(parts):  
                            new_segments.append(parts[i] + parts[i+1])  
                        i += 2  
                        
                    # 处理最后一个可能没有标点的部分  
                    if i < len(parts):  
                        new_segments.append(parts[i])  
                else:  
                    new_segments.append(segment)  
            segments = new_segments  
        
        # 如果分段仍然太少，使用固定长度分割  
        if len(segments) < 3 and len(content) > 80:  
            segments = []  
            chunk_size = min(40, len(content) // 3)  
            for i in range(0, len(content), chunk_size):  
                segments.append(content[i:i+chunk_size])  
        
        return segments  
    
    async def generate_response(  
        self,  
        user_id: int,  
        query: str,  
        flow_type: str = "data_analysis",  
        conversation_id: Optional[str] = None  
    ) -> Dict[str, Any]:  
        try:  
            # 创建会话和消息  
            conversation, message_id = await self.create_chat_message(  
                user_id=user_id,  
                query=query,  
                flow_type=flow_type,  
                conversation_id=conversation_id  
            )  
            
            # 执行流程  
            job_id = str(uuid4())  
            full_response = await self.flow_manager.execute_flow(  
                flow_type=flow_type,  
                job_id=job_id,  
                query=query,  
                user_id=user_id,  
                conversation_id=conversation["id"]  
            )  
            
            # 将 CrewOutput 转换为字符串  
            if hasattr(full_response, 'raw'):  
                full_response = full_response.raw  
            elif not isinstance(full_response, str):  
                full_response = str(full_response)  
            
            # 更新消息  
            await update_message(  
                message_id=message_id,  
                content=full_response  
            )  
            
            # 异步更新会话标题  
            asyncio.create_task(  
                self.update_conversation_title(conversation["id"], query)  
            )  
            
            # 返回结果  
            return {  
                "conversation_id": conversation["id"],  
                "message_id": message_id,  
                "text": full_response,  
                "type": flow_type  
            } 
            
        except Exception as e:
            logger.error(f"生成响应时出错: {str(e)}", exc_info=True)
            raise

    def _process_crew_output(self, result):  
        """处理CrewOutput对象转换为字符串"""  
        if hasattr(result, 'raw'):  
            return result.raw  
        elif not isinstance(result, str):  
            return str(result)  
        return result 