from crewai import Crew, Process  
from app.agents.query_expert import QueryExpertAgent  
from app.agents.database_expert import DatabaseExpertAgent  
from app.agents.data_analyst import DataAnalystAgent  
from app.core.logger import logger  
from app.utils.memory_manager import RedisMemoryManager  
from app.utils.llm_factory import get_llm  
# 导入任务生成器  
from app.tasks import DataAnalysisTasks  

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
        
        # 创建任务生成器  
        self.task_generator = DataAnalysisTasks(  
            self.query_expert_agent,  
            self.database_expert_agent,  
            self.data_analyst_agent  
        )  
    
    def execute(self):  
        """执行数据分析Crew的完整流程 - 同步方法"""  
        try:  
            # 使用同步方法更新状态  
            self._update_progress_sync(  
                self.job_id,  
                5,  
                "启动数据分析流程..."  
            )  
            
            # 使用任务生成器创建任务  
            tasks = self.task_generator.create_tasks(  
                self.query,  
                self.history,  
                self._task_callback_sync  
            )  
            
            # 创建Crew  
            crew = Crew(  
                agents=[  
                    self.query_expert_agent,  
                    self.database_expert_agent,  
                    self.data_analyst_agent  
                ],  
                tasks=tasks,  
                process=Process.sequential,  
                verbose=True,  
            )  
            
            # 添加监听器来检查任务结果  
            def check_task_result(task, output):  
                # 检查输出是否包含错误信息  
                if isinstance(output, str) and any(err in output for err in [  
                    "错误:", "出错:", "执行出错:", "执行统计分析时出错", "生成数据可视化时出错",  
                    "NameError:", "TypeError:", "AttributeError:", "ValueError:"  
                ]):  
                    # 记录错误信息  
                    error_msg = f"任务 {task.description} 失败: {output[:100]}..."  
                    logger.error(error_msg)  
                    # 引发异常以中断整个执行流程  
                    raise Exception(error_msg)  
                return output  
            
            # 为每个任务添加结果检查  
            for task in tasks:  
                original_callback = task.callback  
                
                def wrapped_callback(task_obj, orig_cb):  
                    def wrapper(output):  
                        # 先检查输出  
                        result = check_task_result(task_obj, output.raw if hasattr(output, 'raw') else str(output))  
                        # 如果没有引发异常，则调用原始回调  
                        if orig_cb:  
                            return orig_cb(output)  
                        return output  
                    return wrapper  
                
                task.callback = wrapped_callback(task, original_callback)  
            
            # 启动Crew  
            result = crew.kickoff()  
            
            # 处理结果，确保它是字符串  
            result_str = result.raw if hasattr(result, 'raw') else str(result)  
            
            # 最后再检查一次结果是否包含错误信息  
            if self._is_error_result(result_str):  
                error_msg = f"执行结果包含错误: {result_str[:200]}..."  
                logger.error(error_msg)  
                self._update_progress_sync(  
                    self.job_id,  
                    -1,  
                    error_msg  
                )  
                return error_msg  
            
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

    def _is_error_result(self, result: str) -> bool:  
        """检查结果是否包含错误信息"""  
        error_indicators = [  
            "错误:", "出错:", "执行出错:", "执行统计分析时出错", "生成数据可视化时出错",  
            "NameError:", "TypeError:", "AttributeError:", "ValueError:",  
            "unsupported operand", "not defined", "NoneType", "object has no attribute"  
        ]  
        
        if not isinstance(result, str):  
            return False  
            
        return any(indicator in result for indicator in error_indicators)  

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