from crewai import Crew, Process, Task  
from app.agents.query_expert import QueryExpertAgent  
from app.agents.database_expert import DatabaseExpertAgent  
from app.agents.data_analyst import DataAnalystAgent  
from app.core.logger import logger  
from app.utils.memory_manager import RedisMemoryManager  
from app.utils.llm_factory import get_llm  

class DataAnalysisCrew:  
    """数据分析Crew - 管理数据分析流程的3个Agent协作"""  
    
    def __init__(self, redis_client, job_id: str, query: str, history: str = ""):  
        self.redis_client = redis_client  
        self.job_id = job_id  
        self.query = query  
        self.history = history  
        self.memory_manager = RedisMemoryManager(redis_client)  
        self.llm = get_llm()  
        
        # 创建三个Agent  
        self.query_expert_agent = QueryExpertAgent().get_agent(self.llm)  
        self.database_expert_agent = DatabaseExpertAgent().get_agent(self.llm)  
        self.data_analyst_agent = DataAnalystAgent().get_agent(self.llm)  
    
    def execute(self):  
        """执行数据分析Crew的完整流程 - 同步方法"""  
        try:  
            # 使用同步方法更新状态  
            self._update_progress_sync(  
                self.job_id,  
                5,  
                "启动数据分析流程..."  
            )  
            
            # 创建任务  
            sql_translation_task = Task(  
                description=f"将业务问题转化为SQL查询\n\n用户问题: {self.query}\n\n历史对话: {self.history}",  
                expected_output="优化的SQL查询语句",  
                agent=self.query_expert_agent,  
                async_execution=False,  
                callback=self._task_callback_sync("将业务问题转化为SQL查询", 15)  
            )  
            
            sql_execution_task = Task(  
                description="执行SQL查询并获取结果",  
                expected_output="格式化的查询结果",  
                agent=self.database_expert_agent,  
                async_execution=False,  
                context=[sql_translation_task],  
                callback=self._task_callback_sync("执行SQL查询", 30)  
            )  
            
            data_preprocessing_task = Task(  
                description="对查询结果进行数据整合与预处理",  
                expected_output="预处理后的数据集，包括处理缺失值、异常值和数据规范化",  
                agent=self.database_expert_agent,  
                async_execution=False,  
                context=[sql_execution_task],  
                callback=self._task_callback_sync("数据整合与预处理", 45)  
            )  
            
            statistical_analysis_task = Task(  
                description="进行数据探索与统计分析",  
                expected_output="详细的统计分析结果，包括关键指标、相关性和模式",  
                agent=self.data_analyst_agent,  
                async_execution=False,  
                context=[data_preprocessing_task],  
                callback=self._task_callback_sync("数据探索与统计分析", 60)  
            )  
            
            visualization_task = Task(  
                description="生成数据可视化和洞察",  
                expected_output="可视化结果和关键洞察的详细描述",  
                agent=self.data_analyst_agent,  
                async_execution=False,  
                context=[statistical_analysis_task],  
                callback=self._task_callback_sync("可视化与洞察生成", 75)  
            )  
            
            marketing_suggestions_task = Task(  
                description="基于数据分析生成营销建议",  
                expected_output="详细的营销建议，包括目标用户、营销时机和渠道策略",  
                agent=self.data_analyst_agent,  
                async_execution=False,  
                context=[visualization_task],  
                callback=self._task_callback_sync("营销建议生成", 90)  
            )  
            
            # 创建Crew  
            crew = Crew(  
                agents=[  
                    self.query_expert_agent,  
                    self.database_expert_agent,  
                    self.data_analyst_agent  
                ],  
                tasks=[  
                    sql_translation_task,  
                    sql_execution_task,  
                    data_preprocessing_task,  
                    statistical_analysis_task,  
                    visualization_task,  
                    marketing_suggestions_task  
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
            error_message = f"数据分析Crew执行错误: {str(e)}"  
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