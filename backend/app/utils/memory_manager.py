import json  
import logging  
import time 
from typing import Dict, List, Optional, Any  
import redis.asyncio as aioredis  

logger = logging.getLogger(__name__)  

class RedisMemoryManager:  
    """使用Redis管理对话历史和会话状态"""  
    
    def __init__(self, redis_client):  
        self.redis = redis_client  
        self.prefix = "gold_trading:"  
        self.conversation_prefix = f"{self.prefix}conversation:"  
        self.job_prefix = f"{self.prefix}job:"  
        self.expiration = 60 * 60 * 24 * 7  # 7天过期  
        
    async def save_conversation_history(self, conversation_id: str, messages: List[Dict[str, Any]]) -> bool:  
        """保存对话历史到Redis"""  
        key = f"{self.conversation_prefix}{conversation_id}:history"  
        try:  
            await self.redis.set(key, json.dumps(messages), ex=self.expiration)  
            return True  
        except Exception as e:  
            logger.error(f"保存对话历史失败: {str(e)}")  
            return False  
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:  
        """从Redis获取对话历史"""  
        key = f"{self.conversation_prefix}{conversation_id}:history"  
        try:  
            data = await self.redis.get(key)  
            if data:  
                return json.loads(data)  
            return []  
        except Exception as e:  
            logger.error(f"获取对话历史失败: {str(e)}")  
            return []  
    
    async def append_message(self, conversation_id: str, role: str, content: Any):  
        """添加消息到会话历史"""  
        try:  
            # 处理CrewOutput对象  
            if hasattr(content, 'raw'):  
                content_text = content.raw  
            elif not isinstance(content, str):  
                content_text = str(content)  
            else:  
                content_text = content  
                
            # 构建消息  
            message = {  
                "role": role,  
                "content": content_text,  
                "timestamp": time.time()  
            }  
            
            # 序列化消息  
            message_json = json.dumps(message)  
            
            # 将消息添加到列表  
            history_key = f"history:{conversation_id}"  
            await self.redis.rpush(history_key, message_json)  
            
            # 设置过期时间（7天）  
            await self.redis.expire(history_key, 60 * 60 * 24 * 7)  
            
            return True  
        except Exception as e:  
            logger.error(f"保存对话历史失败: {str(e)}")  
            return False   
    
    async def clear_conversation_history(self, conversation_id: str) -> bool:  
        """清除对话历史"""  
        key = f"{self.conversation_prefix}{conversation_id}:history"  
        try:  
            await self.redis.delete(key)  
            return True  
        except Exception as e:  
            logger.error(f"清除对话历史失败: {str(e)}")  
            return False  
    
    async def save_job_data(self, job_id: str, data: Dict[str, Any]) -> bool:  
        """保存作业数据到Redis"""  
        key = f"{self.job_prefix}{job_id}"  
        try:  
            await self.redis.set(key, json.dumps(data), ex=self.expiration)  
            return True  
        except Exception as e:  
            logger.error(f"保存作业数据失败: {str(e)}")  
            return False  
    
    async def get_job_data(self, job_id: str) -> Optional[Dict[str, Any]]:  
        """从Redis获取作业数据"""  
        key = f"{self.job_prefix}{job_id}"  
        try:  
            data = await self.redis.get(key)  
            if data:  
                return json.loads(data)  
            return None  
        except Exception as e:  
            logger.error(f"获取作业数据失败: {str(e)}")  
            return None  
    
    async def update_job_progress(self, job_id: str, progress: int, output: Any):  
        """更新作业进度和当前输出"""  
        try:  
            # 处理CrewOutput对象  
            if hasattr(output, 'raw'):  
                output_text = output.raw  
            elif not isinstance(output, str):  
                output_text = str(output)  
            else:  
                output_text = output  
                
            # 更新作业数据  
            job_data = {  
                "progress": progress,  
                "current_output": output_text,  
                "status": "ERROR" if progress < 0 else ("COMPLETED" if progress >= 100 else "RUNNING")  
            }  
            
            await self.save_job_data(job_id, job_data)  
            return True  
        except Exception as e:  
            logger.error(f"更新作业进度失败: {str(e)}")  
            return False  
    
    async def get_job_progress(self, job_id: str) -> int:  
        """获取作业进度"""  
        job_data = await self.get_job_data(job_id)  
        if job_data:  
            return job_data.get("progress", 0)  
        return 0  
    
    async def get_job_current_output(self, job_id: str) -> str:  
        """获取作业当前输出"""  
        job_data = await self.get_job_data(job_id)  
        if job_data:  
            return job_data.get("current_output", "")  
        return ""  