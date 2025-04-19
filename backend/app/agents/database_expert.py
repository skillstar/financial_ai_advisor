from crewai import Agent  
from typing import Optional, List, Dict, Any  
from app.core.logger import logger  
# 从tools包导入工具  
from app.tools import ExecuteSQLTool, PreprocessDataTool  

class DatabaseExpertAgent:  
    """数据库执行专家Agent类"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        tools = [  
            ExecuteSQLTool(),  
            PreprocessDataTool()  
        ]  
        
        return Agent(  
            role="数据库执行专家",  
            goal="高效执行SQL查询并进行初步数据整理",  
            backstory="你精通数据库操作和数据整合，能够确保查询执行正确并提供干净的数据集供分析使用。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  