from crewai import Agent  
from typing import Optional, List, Dict, Any  
from app.core.logger import logger  
# 从tools包导入工具  
from app.tools import AnalyzeUserProfilesTool, DevelopMarketingStrategyTool  

class MarketingAnalystAgent:  
    """营销策略分析师Agent类"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        tools = [  
            AnalyzeUserProfilesTool(),  
            DevelopMarketingStrategyTool()  
        ]  
        
        return Agent(  
            role="营销策略分析师",  
            goal="解读用户数据，制定精准营销战略",  
            backstory="作为营销领域的精英，你善于分析用户行为并将数据转化为实际可行的营销策略，帮助企业提高转化率。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  