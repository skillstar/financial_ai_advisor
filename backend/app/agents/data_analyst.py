from crewai import Agent  
from typing import Optional, List, Dict, Any, ClassVar  
from app.core.logger import logger  
# 从tools包直接导入工具，与其他Agent文件保持一致  
from app.tools import (  
    StatisticalAnalysisTool,  
    DataVisualizationTool,   
    MarketingSuggestionsTool,  
    ChartGenerationTool  
) 

class DataAnalystAgent:  
    """数据分析师Agent类"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        tools = [  
            StatisticalAnalysisTool(),  
            DataVisualizationTool(),  
            MarketingSuggestionsTool(),  
            ChartGenerationTool() 
        ]  
        
        return Agent(  
            role="数据分析师",  
            goal="从数据中提取有价值的洞察和模式，并提供图表可视化配置",  
            backstory="你是一位资深数据分析师，擅长数据可视化、统计分析和预测建模，能从数据中发现业务机会并生成直观的图表配置。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  