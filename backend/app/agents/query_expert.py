from crewai import Agent  
from typing import Optional, List, Dict, Any  
from app.core.logger import logger  
# 从tools包导入工具  
from app.tools import TranslateToSQLTool  # 第一轮测试只需要这一个工具  

class QueryExpertAgent:  
    """查询解析专家Agent类 - 第一轮测试版本 (仅SQL翻译)"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        # 第一轮测试只使用TranslateToSQLTool  
        tools = [  
            TranslateToSQLTool(),  
            # ValidateSQLTool() 暂时移除，第二轮再添加  
        ]  
        
        return Agent(  
            role="SQL查询解析专家",  
            goal="将业务问题精确转化为优化的SQL查询语句",  
            backstory="你是一位经验丰富的数据库专家，深入理解金融数据结构，能够将复杂的业务问题转化为高效的SQL查询。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  