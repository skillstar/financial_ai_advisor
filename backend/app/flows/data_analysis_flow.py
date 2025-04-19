import asyncio  
from typing import Dict, Any, Optional  
from uuid import uuid4  

from app.crews.data_analysis_crew import DataAnalysisCrew  
from app.utils.memory_manager import RedisMemoryManager  
from app.core.logger import logger  

class DataAnalysisFlow:  
    """数据分析Flow - 管理数据分析的完整流程"""  
    
    def __init__(self, redis_client):  
        self.redis_client = redis_client  
        self.memory_manager = RedisMemoryManager(redis_client)  
    
    async def execute(  
        self,   
        job_id: str,   
        query: str,   
        user_id: int,  
        conversation_id: Optional[str] = None,  
        history: str = ""  
    ) -> str:  
        """执行数据分析流程"""  
        try:  
            # 创建数据分析Crew  
            crew = DataAnalysisCrew(  
                redis_client=self.redis_client,  
                job_id=job_id,  
                query=query,  
                history=history  
            )  
            
            # 在线程中运行Crew  
            result = await self._run_crew_in_thread(crew)  
            
            # 如果有会话ID，保存对话历史  
            if conversation_id:  
                await self.memory_manager.append_message(  
                    conversation_id,  
                    "assistant",  
                    result  
                )  
            
            return result  
            
        except Exception as e:  
            logger.error(f"数据分析Flow执行错误: {str(e)}", exc_info=True)  
            await self.memory_manager.save_job_data(job_id, {  
                "progress": -1,  
                "current_output": f"错误: {str(e)}",  
                "status": "ERROR"  
            })  
            raise  
    
    async def _run_crew_in_thread(self, crew):  
        """在线程池中运行Crew，使用共享事件循环"""  
        # 使用线程池执行阻塞操作，但不创建新的事件循环  
        loop = asyncio.get_event_loop()  
        
        # 创建一个执行函数，让crew.execute()在线程中执行  
        def execute_crew():  
            try:  
                return crew.execute()  # 直接执行，不创建新循环  
            except Exception as e:  
                logger.error(f"Crew执行错误: {str(e)}")  
                return f"执行出错: {str(e)}"  
        
        # 在线程池中执行，不创建新的事件循环  
        result = await loop.run_in_executor(None, execute_crew)  
        return result 