from crewai import Task  
from app.core.logger import logger  

class DataAnalysisTasks:  
    """数据分析相关任务生成器"""  
    
    def __init__(self, query_expert_agent, database_expert_agent, data_analyst_agent):  
        self.query_expert_agent = query_expert_agent  
        self.database_expert_agent = database_expert_agent  
        self.data_analyst_agent = data_analyst_agent  
    
    def create_tasks(self, query, history, callback_factory):  
        """  
        创建数据分析流程的所有任务  
        
        Args:  
            query: 用户查询  
            history: 历史对话内容  
            callback_factory: 用于生成回调函数的工厂函数  
            
        Returns:  
            list: 任务列表  
        """  
        # SQL翻译任务  
        sql_translation_task = Task(  
            description=f"将业务问题转化为SQL查询\n\n用户问题: {query}\n\n历史对话: {history}",  
            expected_output="优化的SQL查询语句",  
            agent=self.query_expert_agent,  
            async_execution=False,  
            callback=callback_factory("将业务问题转化为SQL查询", 15)  
        )  
        
        # SQL执行任务  
        sql_execution_task = Task(  
            description="执行SQL查询并获取结果",  
            expected_output="格式化的查询结果",  
            agent=self.database_expert_agent,  
            async_execution=False,  
            context=[sql_translation_task],  
            callback=callback_factory("执行SQL查询", 30)  
        )  
        
        # 数据预处理任务  
        data_preprocessing_task = Task(  
            description="对查询结果进行数据整合与预处理",  
            expected_output="预处理后的数据集，包括处理缺失值、异常值和数据规范化",  
            agent=self.database_expert_agent,  
            async_execution=False,  
            context=[sql_execution_task],  
            callback=callback_factory("数据整合与预处理", 45)  
        )  
        
        # 统计分析任务  
        statistical_analysis_task = Task(  
            description="进行数据探索与统计分析",  
            expected_output="详细的统计分析结果，包括关键指标、相关性和模式",  
            agent=self.data_analyst_agent,  
            async_execution=False,  
            context=[data_preprocessing_task],  
            callback=callback_factory("数据探索与统计分析", 60)  
        )  
        
        # 可视化任务  
        visualization_task = Task(  
            description="生成数据可视化和洞察",  
            expected_output="可视化结果和关键洞察的详细描述",  
            agent=self.data_analyst_agent,  
            async_execution=False,  
            context=[statistical_analysis_task],  
            callback=callback_factory("可视化与洞察生成", 75)  
        )  
        
        # 营销建议任务  
        marketing_suggestions_task = Task(  
            description="基于数据分析生成营销建议",  
            expected_output="详细的营销建议，包括目标用户、营销时机和渠道策略",  
            agent=self.data_analyst_agent,  
            async_execution=False,  
            context=[visualization_task],  
            callback=callback_factory("营销建议生成", 90)  
        )  
        
        # 返回所有任务列表  
        return [  
            sql_translation_task,  
            sql_execution_task,  
            data_preprocessing_task,  
            statistical_analysis_task,  
            visualization_task,  
            marketing_suggestions_task  
        ]  