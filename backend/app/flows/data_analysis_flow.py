import asyncio  
import json  
from typing import Dict, Any, Optional  
from uuid import uuid4  

from app.crews.data_analysis_crew import DataAnalysisCrew  
from app.tools.chart_generation import ChartGenerationTool  
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
            analysis_result = await self._run_crew_in_thread(crew)  
            
            # 更新进度  
            await self.memory_manager.update_job_progress(  
                job_id,   
                75,   
                f"数据分析完成，正在生成图表配置..."  
            )  
            
            # 生成图表数据  
            chart_data = await self._generate_chart_data(analysis_result)  
            
            # 合并结果  
            combined_result = self._combine_results(analysis_result, chart_data)  
            
            # 更新任务进度为100%  
            await self.memory_manager.update_job_progress(  
                job_id,  
                100,  
                combined_result  
            )  
            
            # 如果有会话ID，保存对话历史  
            if conversation_id:  
                await self.memory_manager.append_message(  
                    conversation_id,  
                    "assistant",  
                    combined_result  
                )  
            
            return combined_result  
            
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
                return {"error": True, "message": f"执行出错: {str(e)}"}  
    
        # 在线程池中执行，不创建新的事件循环  
        result = await loop.run_in_executor(None, execute_crew)  
        
        # 检查结果是否为错误  
        if isinstance(result, dict) and result.get("error") is True:  
            # 向上抛出异常，终止流程  
            raise Exception(result["message"]) 
    
        # 处理CrewOutput对象  
        if hasattr(result, 'raw'):  
            return result.raw  
        elif not isinstance(result, str):  
            return str(result)  
        return result  
    
    async def _generate_chart_data(self, analysis_result: str) -> Dict[str, Any]:  
        """生成图表数据"""  
        try:  
            # 使用图表生成工具  
            chart_tool = ChartGenerationTool()  
            chart_result = chart_tool._run(analysis_result)  
            
            # 解析结果中的JSON部分  
            import re  
            json_match = re.search(r'```json\n([\s\S]*?)\n```', chart_result)  
            
            if json_match:  
                charts_json = json_match.group(1)  
                charts_config = json.loads(charts_json)  
                return {  
                    "raw_chart_result": chart_result,  
                    "charts_config": charts_config  
                }  
            else:  
                logger.warning("无法从图表生成结果中提取JSON数据")  
                return {  
                    "raw_chart_result": chart_result,  
                    "charts_config": []  
                }  
                
        except Exception as e:  
            logger.error(f"生成图表数据时出错: {str(e)}", exc_info=True)  
            return {  
                "error": str(e),  
                "charts_config": []  
            }  
    
    def _combine_results(self, analysis_result: str, chart_data: Dict[str, Any]) -> str:  
        """合并分析结果和图表数据"""  
        try:  
            # 添加前端可用的数据标记  
            if "charts_config" in chart_data and chart_data["charts_config"]:  
                # 构造带有特殊格式的JSON，方便前端识别和提取  
                charts_json = json.dumps(chart_data["charts_config"], ensure_ascii=False)  
                
                combined = f"""  
{analysis_result}  

<charts-data>  
{charts_json}  
</charts-data>  
"""  
                return combined  
            else:  
                # 如果没有有效的图表配置，只返回分析结果  
                return analysis_result  
                
        except Exception as e:  
            logger.error(f"合并结果时出错: {str(e)}", exc_info=True)  
            return analysis_result  # 出错时返回原始分析结果  