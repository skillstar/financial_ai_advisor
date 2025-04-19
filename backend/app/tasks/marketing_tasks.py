from crewai import Task  
from app.core.logger import logger  

class MarketingTasks:  
    """营销战略相关任务生成器"""  
    
    def __init__(self, marketing_analyst_agent, content_creator_agent):  
        self.marketing_analyst_agent = marketing_analyst_agent  
        self.content_creator_agent = content_creator_agent  
    
    def create_tasks(self, data_analysis_result, callback_factory):  
        """  
        创建营销战略流程的所有任务  
        
        Args:  
            data_analysis_result: 数据分析结果  
            callback_factory: 用于生成回调函数的工厂函数  
            
        Returns:  
            list: 任务列表  
        """  
        # 用户画像分析任务  
        user_profile_task = Task(  
            description=f"分析用户画像并定义营销目标\n\n数据分析结果: {data_analysis_result}",  
            expected_output="详细的用户画像分析和明确的营销目标定义",  
            agent=self.marketing_analyst_agent,  
            async_execution=False,  
            callback=callback_factory("用户画像解读与目标定义", 25)  
        )  
        
        # 营销战略制定任务  
        marketing_strategy_task = Task(  
            description="制定完整的营销战略框架",  
            expected_output="详细的营销战略文档，包括渠道策略、活动规划和资源分配",  
            agent=self.marketing_analyst_agent,  
            async_execution=False,  
            context=[user_profile_task],  
            callback=callback_factory("营销战略框架制定", 50)  
        )  
        
        # 创意活动设计任务  
        campaign_design_task = Task(  
            description="设计创意营销活动",  
            expected_output="详细的创意活动方案，包括活动主题、形式和预期效果",  
            agent=self.content_creator_agent,  
            async_execution=False,  
            context=[marketing_strategy_task],  
            callback=callback_factory("创意活动构思", 75)  
        )  
        
        # 营销文案创作任务  
        copywriting_task = Task(  
            description="创作营销文案",  
            expected_output="完整的营销文案，包括标题、正文和行动号召",  
            agent=self.content_creator_agent,  
            async_execution=False,  
            context=[campaign_design_task],  
            callback=callback_factory("营销文案创作", 95)  
        )  
        
        # 返回所有任务列表  
        return [  
            user_profile_task,  
            marketing_strategy_task,  
            campaign_design_task,  
            copywriting_task  
        ]  