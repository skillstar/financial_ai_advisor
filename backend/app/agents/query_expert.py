from crewai import Agent  
from crewai.tools import BaseTool  
from typing import Optional, List, Dict, Any  
from app.core.logger import logger  

class TranslateToSQLTool(BaseTool):  
    """将自然语言转换为SQL的工具"""  
    
    name: str = "TranslateToSQL"  
    description: str = "将自然语言查询转换为SQL查询，输入是用户的业务问题"  
    
    def _run(self, query: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 在实际实现中使用LLM生成SQL  
            prompt = f"""  
            基于用户的业务问题，生成有效的SQL查询语句。  

            用户问题: {query}  

            考虑数据库结构:  
            - users: 保存用户的基本信息和财务状况  
              (user_id, name, age, account_balance, deposit_amount, withdrawal_amount,   
               investment_risk_tolerance, investment_horizon, monthly_income, monthly_expenses, created_at)  
            - transactions: 记录用户的每笔交易（买入和卖出黄金）  
              (transaction_id, user_id, transaction_type, amount, transaction_date, price_per_ounce)  
            - products: 存储黄金产品信息  
              (product_id, product_name, price_per_ounce, created_at)  
            - user_profiles: 记录用户的投资风险偏好和偏好类型  
              (profile_id, user_id, risk_profile)  

            请生成符合MySQL语法的SQL查询:  
            """  
            
            # 示例SQL (实际应使用LLM) - 已修正以匹配数据库结构  
            sql = """  
            SELECT   
                u.user_id, u.name, up.risk_profile,  
                COUNT(t.transaction_id) as transaction_count,  
                SUM(t.amount) as total_amount,  
                AVG(t.price_per_ounce) as avg_price  
            FROM   
                users u  
            JOIN   
                user_profiles up ON u.user_id = up.user_id  
            LEFT JOIN   
                transactions t ON u.user_id = t.user_id  
            GROUP BY   
                u.user_id, u.name, up.risk_profile  
            ORDER BY   
                total_amount DESC  
            LIMIT 100;  
            """  
            
            return sql  
        except Exception as e:  
            logger.error(f"SQL转换失败: {str(e)}")  
            return f"转换SQL时出错: {str(e)}"  

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

class QueryExpertAgent:  
    """查询解析专家Agent类"""  
    
    def get_agent(self, llm):  
        """创建并返回Agent实例"""  
        # 使用自定义工具类  
        tools = [  
            TranslateToSQLTool(),  
            ValidateSQLTool()  
        ]  
        
        return Agent(  
            role="SQL查询解析专家",  
            goal="将业务问题精确转化为优化的SQL查询语句",  
            backstory="你是一位经验丰富的数据库专家，深入理解金融数据结构，能够将复杂的业务问题转化为高效的SQL查询。",  
            verbose=True,  
            llm=llm,  
            tools=tools  
        )  