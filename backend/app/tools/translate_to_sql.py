# 修改 app/tools/translate_to_sql.py  

from crewai.tools import BaseTool  
from typing import Optional, List, Dict, Any  
from app.core.logger import logger  
import json  

class TranslateToSQLTool(BaseTool):  
    """将自然语言转换为SQL的工具"""  
    
    name: str = "TranslateToSQL"  
    description: str = "将自然语言查询转换为SQL查询，输入是用户的业务问题。每个问题只能调用一次。"  
    
    # 跟踪已处理的查询和对应结果  
    _processed_queries = {}  
    
    def _run(self, query: str) -> str:  
        """实现必需的_run方法"""  
        try:  
            # 尝试解析JSON输入，提取query字段  
            try:  
                # 如果输入是JSON字符串，解析它  
                if isinstance(query, str) and (query.startswith('{') or query.startswith('{')):  
                    parsed = json.loads(query)  
                    if isinstance(parsed, dict) and 'query' in parsed:  
                        query = parsed['query']  
            except:  
                # 解析失败，使用原始输入  
                pass  
                
            # 检查是否已处理过此查询  
            if query in self._processed_queries:  
                return "此查询已被处理过。请修改查询或尝试其他方法。"  

            # 记录查询，防止重复处理  
            self._processed_queries[query] = True  
            
            # 根据不同查询生成不同SQL (简单模拟LLM行为)  
            if "总交易额超过" in query and "交易次数超过" in query and "最近半年" in query:  
                sql = """  
                SELECT COUNT(DISTINCT user_id) AS qualified_user_count  
                FROM (  
                    SELECT   
                        user_id,  
                        SUM(amount) AS total_amount,  
                        COUNT(transaction_id) AS transaction_count,  
                        MAX(transaction_date) AS last_transaction_date  
                    FROM transactions  
                    WHERE transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)  
                    GROUP BY user_id  
                    HAVING   
                        SUM(amount) > 10000   
                        AND COUNT(transaction_id) > 5  
                ) AS qualified_users;  
                """  
            elif "风险偏好" in query:  
                sql = """  
                SELECT   
                    up.risk_profile,  
                    COUNT(DISTINCT u.user_id) AS user_count,  
                    AVG(u.account_balance) AS avg_balance  
                FROM  
                    users u  
                JOIN  
                    user_profiles up ON u.user_id = up.user_id  
                GROUP BY  
                    up.risk_profile  
                ORDER BY   
                    avg_balance DESC;  
                """  
            else:  
                # 默认查询  
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