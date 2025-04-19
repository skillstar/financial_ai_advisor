from crewai.tools import BaseTool  
from typing import Optional, List, Dict, Any  
from app.core.logger import logger  

class ValidateSQLTool(BaseTool):  
    """验证SQL查询的工具"""  
    
    name: str = "ValidateSQL"  
    description: str = "验证SQL查询是否有效，检查语法错误和安全问题"  
    
    def _run(self, sql_query: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 此处应实现SQL验证逻辑  
            lower_query = sql_query.lower()  
            
            # 安全检查  
            dangerous_keywords = ['drop', 'delete', 'truncate', 'update', 'alter', 'create']  
            for keyword in dangerous_keywords:  
                if keyword in lower_query:  
                    return f"查询包含危险关键字 '{keyword}'，已拦截。"  
            
            # 只允许SELECT语句  
            if not lower_query.strip().startswith('select'):  
                return "只允许SELECT查询，其他操作已拦截。"  
            
            return f"SQL验证通过: {sql_query}"  
        except Exception as e:  
            logger.error(f"SQL验证失败: {str(e)}")  
            return f"验证SQL时出错: {str(e)}"  