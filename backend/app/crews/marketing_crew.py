from crewai import Crew, Process, Task  
from app.agents.marketing_analyst import MarketingAnalystAgent  
from app.agents.content_creator import ContentCreatorAgent  
from app.core.logger import logger  
from app.utils.memory_manager import RedisMemoryManager  
from app.utils.llm_factory import get_llm  

class MarketingCrew:  
    """营销战略Crew - 管理营销战略制定流程的2个Agent协作"""  
    
    def __init__(self, redis_client, job_id: str, data_analysis_result: str):  
        self.redis_client = redis_client  
        self.job_id = job_id  
        self.data_analysis_result = data_analysis_result  
        self.memory_manager = RedisMemoryManager(redis_client)  
        self.llm = get_llm()  
        
        # 创建两个Agent  
        self.marketing_analyst_agent = MarketingAnalystAgent().get_agent(self.llm)  
        self.content_creator_agent = ContentCreatorAgent().get_agent(self.llm)  
    
    def execute(self):  
        """执行营销战略Crew的完整流程 - 同步方法"""  
        try:  
            # 使用同步方法更新状态  
            self._update_progress_sync(  
                self.job_id,  
                5,  
                "启动营销战略制定流程..."  
            )  
            
            # 创建任务  
            user_profile_task = Task(  
                description=f"分析用户画像并定义营销目标\n\n数据分析结果: {self.data_analysis_result}",  
                expected_output="详细的用户画像分析和明确的营销目标定义",  
                agent=self.marketing_analyst_agent,  
                async_execution=False,  
                callback=self._task_callback_sync("用户画像解读与目标定义", 25)  
            )  
            
            marketing_strategy_task = Task(  
                description="制定完整的营销战略框架",  
                expected_output="详细的营销战略文档，包括渠道策略、活动规划和资源分配",  
                agent=self.marketing_analyst_agent,  
                async_execution=False,  
                context=[user_profile_task],  
                callback=self._task_callback_sync("营销战略框架制定", 50)  
            )  
            
            campaign_design_task = Task(  
                description="设计创意营销活动",  
                expected_output="详细的创意活动方案，包括活动主题、形式和预期效果",  
                agent=self.content_creator_agent,  
                async_execution=False,  
                context=[marketing_strategy_task],  
                callback=self._task_callback_sync("创意活动构思", 75)  
            )  
            
            copywriting_task = Task(  
                description="创作营销文案",  
                expected_output="完整的营销文案，包括标题、正文和行动号召",  
                agent=self.content_creator_agent,  
                async_execution=False,  
                context=[campaign_design_task],  
                callback=self._task_callback_sync("营销文案创作", 95)  
            )  
            
            # 创建Crew  
            crew = Crew(  
                agents=[  
                    self.marketing_analyst_agent,  
                    self.content_creator_agent  
                ],  
                tasks=[  
                    user_profile_task,  
                    marketing_strategy_task,  
                    campaign_design_task,  
                    copywriting_task  
                ],  
                process=Process.sequential,  
                verbose=True,  
            )  
            
            # 启动Crew  
            result = crew.kickoff()  
            
            # 处理结果，确保它是字符串  
            result_str = result.raw if hasattr(result, 'raw') else str(result)  
            
            # 更新最终结果（使用同步方法）  
            self._update_progress_sync(  
                self.job_id,  
                100,  
                result_str  
            )  
            
            return result_str  
            
        except Exception as e:  
            error_message = f"营销战略Crew执行错误: {str(e)}"  
            logger.error(error_message, exc_info=True)  
            self._update_progress_sync(  
                self.job_id,  
                -1,  
                error_message  
            )  
            return f"处理您的请求时出现错误: {str(e)}"  

    def _update_progress_sync(self, job_id, progress, output):  
        """同步版本的进度更新函数"""  
        # 使用Redis直接存储，不使用异步  
        import json  
        import redis  
        from app.core.config import settings  # 直接导入配置  
        
        try:  
            # 使用配置中的Redis URL创建同步客户端  
            r = redis.Redis.from_url(  
                settings.REDIS_URL,  # 直接使用配置中的URL  
                decode_responses=True  
            )  
            
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
            
            # 保存到Redis  
            key = f"gold_trading:job:{job_id}"  
            r.set(key, json.dumps(job_data), ex=60*60*24*7)  # 7天过期  
            
            return True  
        except Exception as e:  
            logger.error(f"同步更新作业进度失败: {str(e)}")  
            return False  

    def _task_callback_sync(self, task_name, progress):  
        """生成同步任务回调函数"""  
        def callback_func(output):  
            self._update_progress_sync(  
                self.job_id,  
                progress,  
                f"完成任务: {task_name}\n\n{output.raw if hasattr(output, 'raw') else str(output)}"  
            )  
            return output  
        return callback_func  
    
    def _task_callback(self, task_name, progress):  
        """生成任务回调函数"""  
        async def callback_func(output):  
            await self.memory_manager.update_job_progress(  
                self.job_id,   
                progress,   
                f"完成任务: {task_name}\n\n{output.raw}"  
            )  
            return output  
        return callback_func  