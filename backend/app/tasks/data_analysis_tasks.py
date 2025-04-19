from crewai import Task  
from app.core.logger import logger  

class DataAnalysisTasks:  
    """数据分析相关任务生成器 - 第一轮测试版本 (仅SQL翻译)"""  
    
    def __init__(self, query_expert_agent, database_expert_agent=None, data_analyst_agent=None):  
        self.query_expert_agent = query_expert_agent  
        # 第一轮测试不需要这些agent，但保留参数以保持接口一致性  
        self.database_expert_agent = database_expert_agent  
        self.data_analyst_agent = data_analyst_agent  
    
    def create_tasks(self, query, history, callback_factory):  
        """  
        创建第一轮测试的任务 (仅SQL翻译任务)  
        
        Args:  
            query: 用户查询  
            history: 历史对话内容  
            callback_factory: 用于生成回调函数的工厂函数  
            
        Returns:  
            list: 任务列表  
        """  
        # 只保留SQL翻译任务  
        sql_translation_task = Task(  
            description=f"将业务问题转化为SQL查询\n\n用户问题: {query}\n\n历史对话: {history}",  
            expected_output="优化的SQL查询语句",  
            agent=self.query_expert_agent,  
            async_execution=False,  
            callback=callback_factory("将业务问题转化为SQL查询", 100)  # 注意进度改为100%，因为这是唯一任务  
        )  
        
        # 只返回SQL翻译任务  
        return [sql_translation_task]  