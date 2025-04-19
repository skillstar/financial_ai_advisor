from crewai import Agent  
from typing import Optional, List, Dict, Any, ClassVar  
from app.core.logger import logger  
# 从tools包导入工具  
from app.tools import DesignCampaignTool, CreateMarketingCopyTool  

class ContentCreatorAgent:  
    """首席创意内容创作师Agent类"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        tools = [  
            DesignCampaignTool(),  
            CreateMarketingCopyTool()  
        ]  
        
        return Agent(  
            role="首席创意内容创作师",  
            goal="根据营销战略，创造吸引人的活动和文案",  
            backstory="你是内容创意大师，擅长将枯燥的数据和策略转化为吸引人的故事和文案，使营销活动更具吸引力。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  