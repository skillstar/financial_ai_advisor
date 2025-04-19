# app/api/sse.py  
import asyncio  
import json  
import time  
import re  
from typing import AsyncIterable, Dict, Any, Optional  
from fastapi import HTTPException  
from uuid import uuid4  

class StreamManager:  
    """流式响应管理器，处理事件流的生成和发送"""  
    
    @staticmethod  
    async def generate_stream_response(  
        flow_manager,   
        user_id: int,   
        query: str,  
        flow_type: str = "data_analysis"  
    ) -> AsyncIterable[str]:  
        """生成流式响应"""  
        total_start_time = time.time()  
        
        # 创建唯一作业ID  
        job_id = str(uuid4())  
        
        # 发送初始处理消息  
        try:  
            # 发送处理中消息  
            processing_data = {  
                'text': "正在处理您的问题，请稍候...",  
                'job_id': job_id,  
                'type': flow_type  
            }  
            yield f"data: {json.dumps(processing_data, ensure_ascii=False)}\n\n"  
            
            # 启动作业处理但不等待完成  
            flow_task = asyncio.create_task(  
                flow_manager.execute_flow(  
                    flow_type=flow_type,  
                    job_id=job_id,  
                    query=query,  
                    user_id=user_id  
                )  
            )  
            
            # 模拟进度更新  
            progress = 0  
            last_update = ""  
            
            # 监控作业进度并发送更新  
            while not flow_task.done():  
                # 获取当前进度  
                current_progress = await flow_manager.get_job_progress(job_id)  
                current_text = await flow_manager.get_job_current_output(job_id)  
                
                # 如果有新的进度或输出，发送更新  
                if current_progress > progress or current_text != last_update:  
                    progress = current_progress  
                    last_update = current_text  
                    
                    update_data = {  
                        'text': current_text,  
                        'job_id': job_id,  
                        'progress': progress,  
                        'type': flow_type  
                    }  
                    yield f"data: {json.dumps(update_data, ensure_ascii=False)}\n\n"  
                
                # 短暂等待  
                await asyncio.sleep(0.5)  
            
            # 获取最终结果  
            result = await flow_task  
            
            # 发送完成消息  
            complete_data = {  
                'text': result,  
                'job_id': job_id,  
                'end': True,  
                'type': flow_type,  
                'duration': round(time.time() - total_start_time, 2)  
            }  
            yield f"data: {json.dumps(complete_data, ensure_ascii=False)}\n\n"  
            
        except Exception as e:  
            # 发送错误消息  
            error_data = {  
                'text': f"处理您的请求时出错: {str(e)}",  
                'job_id': job_id,  
                'end': True,  
                'error': True  
            }  
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"  